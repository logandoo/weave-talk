declare module 'simple-rnnoise-wasm' {
  export interface RNNoiseAssets {
    module: WebAssembly.Module
  }

  export function rnnoise_loadAssets(opts?: {
    scriptSrc?: string
    moduleSrc?: string
  }): Promise<RNNoiseAssets>

  export class RNNoiseNode extends AudioWorkletNode {
    constructor(context: BaseAudioContext)
    static ready: boolean
    static register(ctx: BaseAudioContext, assets?: RNNoiseAssets): Promise<void>
    update(enabled?: boolean): void
    onstatus: ((ev: Event) => void) | null
  }
}
