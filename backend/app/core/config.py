import os
import toml
from pathlib import Path
from typing import Optional
from functools import lru_cache


def _parse_int(value) -> Optional[int]:
    if value == "" or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config.toml"
            )

        self.config_path = Path(config_path).resolve()
        self._config = toml.load(config_path)
        # Model config split: every model-related setting (LLM / ASR / TTS /
        # embedding / rerank / judge / verifier / subagent / validator /
        # memory / title / providers) lives in config_model.toml, merged
        # OVER the main file so config.toml stays a pure infra file. When the
        # model file is absent (legacy deployments) the main file's sections
        # remain authoritative — every property below is unchanged.
        self.model_config_path = self._resolve_model_config_path(config_path)
        self._config = self._merge_model_config(self._config)

    @staticmethod
    def _resolve_model_config_path(config_path: str) -> Optional[Path]:
        env_override = os.environ.get("CONFIG_MODEL_PATH")
        if env_override:
            return Path(env_override).resolve()
        main = Path(config_path).resolve()
        candidate = main.parent / "config_model.toml"
        return candidate if candidate.exists() else None

    # Sections that belong to config_model.toml. Whole-section moves:
    _MODEL_SECTIONS = {
        "api",               # legacy main LLM endpoint
        "defaults",          # default LLM sampling params
        "default_assistant", # assistant-scoped sampling params
        "asr",               # speech recognition models
        "voice",             # voice LLM / TTS / ASR tuning
        "providers",         # multi-provider LLM routing
        "deathmatch",        # judge / verifier models + goal-loop budgets
        "sub_agent",         # subagent LLM params
        "title_generation",  # title LLM params
        "memory",            # memory LLM / embedding / rerank / cost models
    }
    # [agent] stays in the main file for harness tuning, but its MODEL
    # sub-sections move. Only these keys are taken from the model file.
    _MODEL_AGENT_SUBSECTIONS = {
        "auxiliary",      # per-task auxiliary models (coordinator/classifier/title/…)
        "compression",    # context-compression model params
        "moa",            # mixture-of-agents models
        "memory",         # daily summary / dream models
        "tool_digest",    # subagent tool-result digest model
        "sub_agent",      # subagent model params
    }

    def _merge_model_config(self, base: dict) -> dict:
        if self.model_config_path is None:
            return base
        import logging
        logger = logging.getLogger(__name__)
        try:
            model_cfg = toml.load(self.model_config_path)
        except Exception:
            logger.exception(
                "Failed to load %s — falling back to main config sections. "
                "If this deployment was already split, the server is now "
                "running with EMPTY/default model config and will fail on "
                "the first LLM call.",
                self.model_config_path,
            )
            return base
        merged = dict(base)
        for section in self._MODEL_SECTIONS:
            if section in model_cfg:
                if section in merged:
                    # Section-granular replacement: a partial model file
                    # REPLACES the whole main-file section. Warn so ops can
                    # spot missing keys (e.g. a hand-crafted model file with
                    # only [api].model_name would silently drop base_url/key).
                    logger.warning(
                        "config_model.toml section [%s] REPLACES the main "
                        "config.toml section of the same name (whole-section "
                        "override, not per-key merge)", section,
                    )
                merged[section] = model_cfg[section]
        if "agent" in model_cfg:
            agent = dict(merged.get("agent") or {})
            for key, value in (model_cfg.get("agent") or {}).items():
                if key in self._MODEL_AGENT_SUBSECTIONS:
                    agent[key] = value
            merged["agent"] = agent
        return merged

    @property
    def database_type(self) -> str:
        """数据库后端：sqlite（默认，本地轻量）| postgres（与 chatbot 一致的 asyncpg）。"""
        t = str(self._config.get("database", {}).get("type", "sqlite")).strip().lower()
        if t not in ("sqlite", "postgres"):
            raise ValueError(
                f"[database].type 非法值 {t!r}（仅支持 sqlite / postgres）"
            )
        return t

    @property
    def database_url(self) -> str:
        db = self._config.get("database", {})
        if self.database_type == "sqlite":
            # path 相对于 backend/（config.toml 所在目录）解析为绝对路径，
            # 避免依赖启动时的 cwd；绝对路径需 4 斜杠（sqlite+aiosqlite:/// + /abs）。
            raw_path = db.get("path", "weave_talk.db")
            return "sqlite+aiosqlite:///" + str((self.backend_root / raw_path).resolve())
        host = db.get("host", "localhost")
        port = db.get("port", 5432)
        username = db.get("username", "postgres")
        password = db.get("password", "")
        name = db.get("name", "chatllm")
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}"

    @property
    def database_pool_size(self) -> int:
        return int(self._config.get("database", {}).get("pool_size", 20))

    @property
    def database_max_overflow(self) -> int:
        return int(self._config.get("database", {}).get("max_overflow", 30))

    @property
    def database_pool_recycle(self) -> int:
        return int(self._config.get("database", {}).get("pool_recycle", 1800))

    @property
    def database_pool_timeout(self) -> int:
        return int(self._config.get("database", {}).get("pool_timeout", 30))

    @property
    def api_base_url(self) -> str:
        return self._config.get("api", {}).get("base_url", "https://api.openai.com/v1")

    @property
    def api_key(self) -> Optional[str]:
        key = self._config.get("api", {}).get("api_key", "")
        return key if key else None

    @property
    def security(self) -> dict:
        return self._config.get("security", {})

    @property
    def security_jwt_secret_key(self) -> Optional[str]:
        key = self.security.get("jwt_secret_key", "")
        if key:
            return key
        return os.environ.get("JWT_SECRET_KEY") or None

    @property
    def security_cors_allow_origins(self) -> list:
        origins = self.security.get("cors_allow_origins", ["*"])
        if isinstance(origins, str):
            return [origins]
        return list(origins)

    @property
    def security_cors_allow_credentials(self) -> bool:
        return bool(self.security.get("cors_allow_credentials", True))

    @property
    def super_admin_bypass(self) -> bool:
        return bool(self.security.get("super_admin_bypass", False))

    @property
    def model_name(self) -> Optional[str]:
        return self._config.get("api", {}).get("model_name") or None

    @property
    def server_host(self) -> str:
        return self._config.get("server", {}).get("host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        return self._config.get("server", {}).get("port", 8158)

    @property
    def server_scheme(self) -> str:
        """Match the SSL auto-detection in scripts/start.sh: when key.pem and
        cert.pem exist in the backend directory, uvicorn is launched with
        --ssl-keyfile/--ssl-certfile, so the API is https."""
        key_pem = self.backend_root / "key.pem"
        cert_pem = self.backend_root / "cert.pem"
        return "https" if (key_pem.exists() and cert_pem.exists()) else "http"

    @property
    def deathmatch_self_eval_username(self) -> str:
        return str(self.deathmatch.get("self_eval_username", "") or "")

    @property
    def deathmatch_self_eval_password(self) -> str:
        return str(self.deathmatch.get("self_eval_password", "") or "")

    @property
    def project_root(self) -> Path:
        return self.config_path.parent.parent

    @property
    def backend_root(self) -> Path:
        return self.config_path.parent

    @property
    def defaults(self) -> dict:
        return self._config.get("defaults", {})

    @property
    def default_temperature(self) -> float:
        return self.defaults.get("temperature", 0.7)

    @property
    def default_top_p(self) -> float:
        return self.defaults.get("top_p", 1.0)

    @property
    def default_top_k(self) -> Optional[int]:
        val = self.defaults.get("top_k")
        return _parse_int(val)

    @property
    def default_presence_penalty(self) -> float:
        return self.defaults.get("presence_penalty", 0.0)

    @property
    def default_frequency_penalty(self) -> float:
        return self.defaults.get("frequency_penalty", 0.0)

    @property
    def default_max_tokens(self) -> Optional[int]:
        val = self.defaults.get("max_tokens")
        return _parse_int(val)

    @property
    def default_assistant(self) -> dict:
        return self._config.get("default_assistant", {})

    @property
    def default_assistant_name(self) -> str:
        return self.default_assistant.get("name", "默认助手")

    @property
    def default_assistant_system_prompt(self) -> str:
        return self.default_assistant.get("system_prompt", "")

    @property
    def default_assistant_temperature(self) -> float:
        return self.default_assistant.get("temperature", 0.7)

    @property
    def default_assistant_top_p(self) -> float:
        return self.default_assistant.get("top_p", 1.0)

    @property
    def default_assistant_top_k(self) -> Optional[int]:
        val = self.default_assistant.get("top_k")
        return _parse_int(val)

    @property
    def default_assistant_presence_penalty(self) -> float:
        return self.default_assistant.get("presence_penalty", 0.0)

    @property
    def default_assistant_frequency_penalty(self) -> float:
        return self.default_assistant.get("frequency_penalty", 0.0)

    @property
    def default_assistant_max_tokens(self) -> Optional[int]:
        val = self.default_assistant.get("max_tokens")
        return _parse_int(val)

    @property
    def asr(self) -> dict:
        return self._config.get("asr", {})

    @property
    def asr_base_url(self) -> str:
        return self.asr.get("base_url", "")

    @property
    def asr_model(self) -> str:
        return self.asr.get("model", "paraformer-zh")

    @property
    def asr_is_dashscope(self) -> bool:
        return bool(self.asr.get("is_dashscope", False))

    @property
    def asr_is_mimo(self) -> bool:
        return bool(self.asr.get("is_mimo", False))

    @property
    def asr_api_key(self) -> str:
        return self.asr.get("api_key", "")

    @property
    def asr_dashscope_api_key(self) -> str:
        return self.asr.get("dashscope_api_key", "")

    @property
    def asr_dashscope_model(self) -> str:
        return self.asr.get("dashscope_model", "qwen3-asr-flash-realtime-2026-02-10")

    @property
    def voice(self) -> dict:
        return self._config.get("voice", {})

    @property
    def voice_enabled(self) -> bool:
        return bool(self.voice.get("enabled", False))

    @property
    def voice_provider(self) -> str:
        return str(self.voice.get("provider", "default"))

    @property
    def voice_model_name(self) -> str:
        return str(self.voice.get("model_name", ""))

    @property
    def voice_system_prompt(self) -> str:
        return str(self.voice.get("system_prompt", ""))

    @property
    def voice_temperature(self) -> float:
        try:
            return float(self.voice.get("temperature", 0.7))
        except (TypeError, ValueError):
            return 0.7

    @property
    def voice_max_tokens(self) -> Optional[int]:
        return _parse_int(self.voice.get("max_tokens", 1024))

    @property
    def voice_duplex_model(self) -> str:
        return str(self.voice.get("duplex_model", ""))

    @property
    def voice_intent_model(self) -> str:
        return str(self.voice.get("intent_model", ""))

    @property
    def voice_barge_in_enabled(self) -> bool:
        return bool(self.voice.get("barge_in_enabled", True))

    @property
    def voice_bg_task_notify_enabled(self) -> bool:
        """When a background task (submitted from a voice conversation) reaches
        a terminal state, proactively announce it in the live voice session and
        let the assistant offer follow-up actions (read result / export / save)."""
        return bool(self.voice.get("bg_task_notify_enabled", True))

    @property
    def voice_barge_in_onset_min_chars(self) -> int:
        """Minimum utterance length (chars, after stripping punctuation) for
        the acoustic ONSET barge-in pause. Utterances shorter than this
        (e.g. "对"/"嗯是"/"好") are NOT paused — they are overwhelmingly
        backchannels or mic false positives (TTS-echo / environment audio
        misrecognized as a syllable; the echo gate only catches transcripts
        matching the spoken text, so misrecognitions slip through). They
        flow through the normal EoT+classify path instead — a backchannel
        then never interrupts the playback at all. Real interrupts are
        almost always >= this length and still pause immediately."""
        try:
            return int(self.voice.get("barge_in_onset_min_chars", 3))
        except (TypeError, ValueError):
            return 3

    @property
    def voice_barge_in_no_interrupt_seconds(self) -> float:
        """No-interrupt window (s) after a TTS playback burst starts. Utterances
        flushed inside the window are deferred (queued + prefetched) instead of
        cutting playback — the opening instants of a burst are where own-voice
        echo/reverb most often fools ASR. Explicit stop words bypass this."""
        try:
            return float(self.voice.get("barge_in_no_interrupt_seconds", 1.2))
        except (TypeError, ValueError):
            return 1.2

    @property
    def voice_barge_in_cooldown_seconds(self) -> float:
        """Cooldown (s) after each confirmed interrupt. Prevents a single noisy
        stretch (echo tail, reverb, the user's own continuing speech) from
        re-interrupting the resumed playback over and over."""
        try:
            return float(self.voice.get("barge_in_cooldown_seconds", 2.0))
        except (TypeError, ValueError):
            return 2.0

    @property
    def voice_barge_in_onset_enabled(self) -> bool:
        """Acoustic-layer onset barge-in (FireRedChat pVAD pattern): when speech
        is detected during TTS playback, pause the audio IMMEDIATELY on the
        first ASR partial (instead of waiting for EoT + LLM classification,
        ~2s). The barge-in classifier then decides: interrupt -> answer the new
        turn; backchannel/defer -> resume playback from the breakpoint."""
        return bool(self.voice.get("barge_in_onset_enabled", True))

    @property
    def voice_barge_in_proximity_gate(self) -> bool:
        """Acoustic near-field gate for barge-in: the browser classifies its
        mic input as near-field (user close to the phone — almost certainly
        the user's own voice) vs far-field (environment speech — TV/room
        conversation) and reports it via the audio_proximity WS event. When
        enabled, far-field speech never pauses playback (onset) and the
        barge-in classifier receives the near/far evidence. Without the
        signal (unknown clients) the gate defaults to near — old behavior."""
        return bool(self.voice.get("barge_in_proximity_gate", True))

    @property
    def voice_barge_in_proximity_stale_seconds(self) -> float:
        """Freshness window (s) for the near-field signal: a near report older
        than this is treated as far (the client stopped reporting — be
        conservative and never pause on stale evidence)."""
        try:
            return float(self.voice.get("barge_in_proximity_stale_seconds", 1.0))
        except (TypeError, ValueError):
            return 1.0

    @property
    def voice_backchannel_recall_seconds(self) -> float:
        """Window (s) during which a backchannel-classified utterance can
        recall (skip) a queued copy of itself — the window/cooldown defer
        path enqueues turns before the barge-in classifier verdict lands, and
        a late backchannel verdict must prevent the filler from being answered
        as a real turn (ghost-message fix, conv 689f06ec)."""
        try:
            return float(self.voice.get("backchannel_recall_seconds", 30.0))
        except (TypeError, ValueError):
            return 30.0

    @property
    def voice_eot_semantic_enabled(self) -> bool:
        """Semantic end-of-turn: for utterances WITHOUT terminal punctuation,
        probe semantic completeness with an LLM judge once silence passes
        voice_eot_semantic_probe_seconds. "Complete" flushes early (unpunctuated
        finished speech answers faster than the hard silence threshold);
        "incomplete"/error waits for the hard threshold (fail-open, no added
        dead time beyond the current behavior)."""
        return bool(self.voice.get("eot_semantic_enabled", True))

    @property
    def voice_eot_semantic_probe_seconds(self) -> float:
        """Silence (s) after which the semantic EoT judge is consulted for
        unpunctuated text. Must be below voice_eot_silence_incomplete_seconds
        (the hard flush threshold) so the judge can beat it."""
        try:
            return float(self.voice.get("eot_semantic_probe_seconds", 1.0))
        except (TypeError, ValueError):
            return 1.0

    @property
    def voice_eot_paused_probe_seconds(self) -> float:
        """Silence (s) after which the semantic EoT judge is consulted while
        playback is PAUSED (acoustic onset barge-in). The user's reaction is
        the only speech in that state, so the endpoint can be faster without
        fragment risk — the flush is still gated by the judge's verdict.
        Keeps the pause→resume silence inside the user's patience (the
        classify now runs in parallel via the onset pre-classify)."""
        try:
            return float(self.voice.get("eot_paused_probe_seconds", 0.6))
        except (TypeError, ValueError):
            return 0.6

    @property
    def voice_eot_semantic_timeout_seconds(self) -> float:
        """Hard bound (s) on the semantic EoT judge call (gate wait + LLM call).
        On timeout the watchdog falls back to the hard silence threshold —
        never blocks the EoT critical path beyond this bound."""
        try:
            return float(self.voice.get("eot_semantic_timeout_seconds", 1.5))
        except (TypeError, ValueError):
            return 1.5

    @property
    def voice_disable_thinking(self) -> bool:
        """Voice turns force provider reasoning/thinking OFF by default (True),
        for every provider — qwen/DashScope gets enable_thinking=False, others
        get thinking.type=disabled (see voice_service._thinking_off_body).
        Voice latency cannot afford reasoning time; set False only to
        deliberately experiment with reasoning-capable voice turns."""
        return bool(self.voice.get("disable_thinking", True))

    @property
    def voice_tts_enabled(self) -> bool:
        return bool(self.voice.get("tts_enabled", True))

    @property
    def voice_tts_base_url(self) -> str:
        return str(self.voice.get("tts_base_url", ""))

    @property
    def voice_tts_api_key(self) -> str:
        return str(self.voice.get("tts_api_key", ""))

    @property
    def voice_tts_model(self) -> str:
        return str(self.voice.get("tts_model", "mimo-v2.5-tts"))

    @property
    def voice_tts_voice(self) -> str:
        return str(self.voice.get("tts_voice", "冰糖"))

    @property
    def voice_tts_style_instruction(self) -> str:
        return str(self.voice.get("tts_style_instruction", ""))

    @property
    def voice_context_turns(self) -> int:
        try:
            return int(self.voice.get("context_turns", 8))
        except (TypeError, ValueError):
            return 8

    @property
    def voice_eot_silence_seconds(self) -> float:
        """Silence (s) before flushing a turn whose text ends with terminal
        punctuation (a complete-looking utterance). Shorter = more responsive."""
        try:
            return float(self.voice.get("eot_silence_seconds", 0.6))
        except (TypeError, ValueError):
            return 0.6

    @property
    def voice_eot_silence_incomplete_seconds(self) -> float:
        """Silence (s) before flushing a turn whose text does NOT end with
        terminal punctuation (likely a mid-sentence pause). Longer = less
        truncation of long questions spoken with natural pauses. Must cover
        FunASR's long-sentence finalization latency — observed upstream-result
        gaps of 1.6s at sentence boundaries (2026-07-21), so values <= 1.5s
        chop continuous speech at sentence boundaries."""
        try:
            return float(self.voice.get("eot_silence_incomplete_seconds", 2.0))
        except (TypeError, ValueError):
            return 2.0

    @property
    def voice_eot_complete_grace_seconds(self) -> float:
        """Grace period (s) of NO ASR activity after an utterance whose text
        ends with terminal punctuation before the turn flushes. fun-asr-realtime
        emits the first partial of a follow-on sentence ~0.5-1.3s after a
        sentence_end when the user keeps speaking (inter-sentence pause +
        recognition latency), so ~1.2s distinguishes a real stop from a
        sentence boundary mid-speech (0.3s faster per turn than 1.5s; a
        boundary-gap flush is now recovered by the onset barge-in + fragment
        coalescing)."""
        try:
            return float(self.voice.get("eot_complete_grace_seconds", 1.2))
        except (TypeError, ValueError):
            return 1.2

    @property
    def voice_eot_complete_max_seconds(self) -> float:
        """Hard cap (s) on how long a COMPLETE utterance (ends with terminal
        punctuation) may wait for the activity-grace before flushing anyway.
        Bounds the wait in noisy environments where background speech keeps
        feeding ASR activity (which would otherwise postpone the flush
        indefinitely). When the user genuinely continues, the next partial
        removes the terminal punctuation from the tail and resets this timer,
        so it only fires when the text has sat complete for the whole cap."""
        try:
            return float(self.voice.get("eot_complete_max_seconds", 3.0))
        except (TypeError, ValueError):
            return 3.0

    @property
    def voice_fragment_merge_seconds(self) -> float:
        """Probe window (s) for coalescing chopped ASR turns in the responder.
        Queued backlog fragments always merge immediately; while the merged
        text does NOT end with terminal punctuation (evidence the EoT cut a
        continuous utterance mid-speech) the responder waits up to this long
        for the next fragment (re-arming on each arrival). Kept short: a
        single chopped head should be answered quickly and its tail answered
        as a follow-up turn, not stall the head."""
        try:
            return float(self.voice.get("fragment_merge_seconds", 1.0))
        except (TypeError, ValueError):
            return 1.0

    @property
    def voice_fragment_merge_max_seconds(self) -> float:
        """Total cap (s) on fragment coalescing for a single turn — bounds the
        added latency when an utterance is chopped into many fragments."""
        try:
            return float(self.voice.get("fragment_merge_max_seconds", 10.0))
        except (TypeError, ValueError):
            return 10.0

    @property
    def voice_noise_gate_max_chars(self) -> int:
        """Only run the agentic ASR-noise (should_respond) gate for utterances
        of at most this many characters. Longer utterances are always answered
        so a real (long) question is never swallowed as 'noise'."""
        try:
            return int(self.voice.get("noise_gate_max_chars", 3))
        except (TypeError, ValueError):
            return 3

    @property
    def voice_asr_speech_noise_threshold(self) -> float:
        """Fun-ASR VAD speech/noise decision threshold (range [-1.0, 1.0],
        adjust in 0.1 steps per upstream docs). Higher values filter MORE
        audio as noise (less background-voice pickup); values >= 0.5
        misclassify real user speech as noise (verified 2026-07-21),
        producing long upstream-result gaps mid-utterance that the EoT then
        flushes as truncated turns. 0.3 stays the default — the 0.4 bump was
        reverted for lack of real-audio verification (A4.9 C4); background
        speech is gated acoustically by the proximity gate instead. Browser-
        side RNNoise handles denoising."""
        try:
            v = float(self.voice.get("asr_speech_noise_threshold", 0.3))
        except (TypeError, ValueError):
            return 0.3
        return max(-1.0, min(1.0, v))

    @property
    def voice_asr_context_enabled(self) -> bool:
        """Whether to pass recent conversation turns to fun-asr-realtime as
        context (raw_input.context) to bias recognition toward the dialogue
        topic and suppress off-topic background speech."""
        return bool(self.voice.get("asr_context_enabled", True))

    @property
    def voice_asr_context_turns(self) -> int:
        """Number of recent user/assistant turns to include in the fun-asr
        realtime context (DashScope caps each role at 5 messages; per-turn
        text is capped at 400 chars by the service)."""
        try:
            return max(0, min(5, int(self.voice.get("asr_context_turns", 3))))
        except (TypeError, ValueError):
            return 3

    @property
    def voice_intent_context_turns(self) -> int:
        """Number of recent turns the intent subagent sees when judging
        should_respond. More context = better off-topic detection at a small
        prompt-size cost."""
        try:
            return max(0, min(8, int(self.voice.get("intent_context_turns", 4))))
        except (TypeError, ValueError):
            return 4

    @property
    def voice_subagent_timeout_seconds(self) -> float:
        """Timeout for each voice subagent classifier call (barge-in, intent,
        interjection). These run on the user's critical path (barge-in blocks
        turn queuing; a slow interjection check blocks EoT flush), so a long
        bound can make the assistant appear dead for tens of seconds. 6s
        covers the normal 1-2s call plus provider hiccups while bounding the
        worst case; every classifier fail-safes on timeout."""
        try:
            return max(2.0, float(self.voice.get("subagent_timeout_seconds", 6.0)))
        except (TypeError, ValueError):
            return 6.0

    @property
    def voice_llm_retry_attempts(self) -> int:
        """Extra attempts for the voice main LLM stream on provider
        rate-limit errors (429). xiaomimimo hard-limits when a voice session
        fires several LLM calls concurrently (interjection + intent + main);
        without retries the whole turn dies with an error event and the user
        gets no answer. Retries only while nothing has been generated yet."""
        try:
            return max(0, min(4, int(self.voice.get("llm_retry_attempts", 2))))
        except (TypeError, ValueError):
            return 2

    # ---- Interjection (插话) mechanism ----

    @property
    def voice_interjection_enabled(self) -> bool:
        """Whether the agent can interject brief remarks while the user is
        still speaking. When enabled, each completed ASR sentence is sent to
        an interjection subagent that decides whether to make a quick comment."""
        return bool(self.voice.get("interjection_enabled", True))

    @property
    def voice_interjection_model(self) -> str:
        """Model for the interjection subagent. Falls back to the intent model
        if not specified."""
        return str(self.voice.get("interjection_model", ""))

    @property
    def voice_interjection_cooldown_seconds(self) -> float:
        """Minimum seconds between interjections. Prevents the agent from
        interjecting on every single sentence."""
        try:
            return max(0.5, float(self.voice.get("interjection_cooldown_seconds", 3.0)))
        except (TypeError, ValueError):
            return 3.0

    @property
    def voice_interjection_max_per_turn(self) -> int:
        """Maximum interjections during a single user speech turn."""
        try:
            return max(0, int(self.voice.get("interjection_max_per_turn", 3)))
        except (TypeError, ValueError):
            return 3

    @property
    def voice_emotion_enabled(self) -> bool:
        """Whether the agent has an emotional state that affects interjection
        frequency and answer tone. When excited or upset, the agent interjects
        more actively."""
        return bool(self.voice.get("emotion_enabled", True))

    @property
    def sub_agent(self) -> dict:
        return self._config.get("sub_agent", {})

    @property
    def sub_agent_structured_output_attempts(self) -> int:
        return max(1, int(self.sub_agent.get("structured_output_attempts", 3)))

    @property
    def sub_agent_retry_delay_seconds(self) -> float:
        return float(self.sub_agent.get("retry_delay_seconds", 2.0))


    @property
    def title_generation(self) -> dict:
        return self._config.get("title_generation", {})

    @property
    def title_generation_structured_output_attempts(self) -> int:
        return max(
            1,
            int(
                self.title_generation.get(
                    "structured_output_attempts",
                    self.sub_agent_structured_output_attempts,
                )
            ),
        )

    @property
    def title_generation_retry_delay_seconds(self) -> float:
        return float(
            self.title_generation.get(
                "retry_delay_seconds",
                self.sub_agent_retry_delay_seconds,
            )
        )

    @property
    def title_generation_max_tokens(self) -> int:
        return int(self.title_generation.get("max_tokens", 200))

    @property
    def title_generation_repair_max_tokens(self) -> int:
        return int(self.title_generation.get("repair_max_tokens", 320))


    # ---- Providers ----

    @property
    def providers(self) -> dict:
        return self._config.get("providers", {})



@lru_cache()
def get_config() -> Config:
    return Config()


def clear_config_cache() -> None:
    get_config.cache_clear()
