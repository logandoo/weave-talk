
from pydantic import BaseModel


class HotwordItem(BaseModel):
    text: str
    weight: int
    lang: str | None = None


class HotwordListResponse(BaseModel):
    hotwords: list[HotwordItem]


class HotwordListRequest(BaseModel):
    hotwords: list[HotwordItem]


class ASRRequest(BaseModel):
    language: str | None = "auto"
    format: str | None = "wav"
    return_timestamps: bool | None = True
    use_hotwords: bool | None = True
    custom_hotwords: list[HotwordItem] | None = None
    context: str | None = None


class SegmentInfo(BaseModel):
    speaker: str
    speaker_confidence: float | None = None
    start_time: float
    end_time: float
    text: str


class TimestampInfo(BaseModel):
    start_time: float
    end_time: float
    text: str


class ASRResponse(BaseModel):
    text: str
    language: str | None = None
    timestamps: list[TimestampInfo] | None = []
    segments: list[SegmentInfo] | None = []
    hotwords_used: list[str] | None = []
    speaker_mode: str | None = "disabled"
    duration: float | None = None
