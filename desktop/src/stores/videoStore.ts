import { create } from "zustand";
import type { VideoParams } from "../api/types";

interface VideoStore {
  currentStep: number;
  params: Partial<VideoParams>;
  taskId: string | null;
  setStep: (step: number) => void;
  updateParams: (params: Partial<VideoParams>) => void;
  setTaskId: (id: string | null) => void;
  reset: () => void;
}

const DEFAULT_PARAMS: Partial<VideoParams> = {
  video_aspect: "16:9",
  video_concat_mode: "random",
  video_transition_mode: "FadeIn",
  video_clip_duration: 5,
  video_count: 1,
  video_language: "en",
  voice_name: "en-US-AriaNeural-Female",
  voice_volume: 1.0,
  voice_rate: 1.0,
  bgm_volume: 0.2,
  caption_style: "default",
  color_preset: "none",
  subtitle_enabled: true,
  subtitle_position: "bottom",
  font_size: 60,
  n_threads: 2,
  paragraph_number: 1,
};

export const useVideoStore = create<VideoStore>((set) => ({
  currentStep: 0,
  params: { ...DEFAULT_PARAMS },
  taskId: null,
  setStep: (step) => set({ currentStep: step }),
  updateParams: (params) => set((s) => ({ params: { ...s.params, ...params } })),
  setTaskId: (id) => set({ taskId: id }),
  reset: () => set({ currentStep: 0, params: { ...DEFAULT_PARAMS }, taskId: null }),
}));
