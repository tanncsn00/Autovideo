export type VideoAspect = "16:9" | "9:16" | "1:1";
export type VideoConcatMode = "random" | "sequential";
export type VideoTransitionMode = "None" | "Shuffle" | "FadeIn" | "FadeOut" | "SlideIn" | "SlideOut";

export interface VideoParams {
  video_subject?: string;
  video_script?: string;
  video_terms?: string;
  video_aspect?: VideoAspect;
  video_concat_mode?: VideoConcatMode;
  video_transition_mode?: VideoTransitionMode;
  video_clip_duration?: number;
  video_count?: number;
  video_language?: string;
  video_source?: string;

  voice_name?: string;
  voice_volume?: number;
  voice_rate?: number;

  bgm_type?: string;
  bgm_file?: string;
  bgm_volume?: number;

  subtitle_enabled?: boolean;
  subtitle_position?: string;
  custom_position?: number;
  font_name?: string;
  text_fore_color?: string;
  text_background_color?: string;
  font_size?: number;
  stroke_color?: string;
  stroke_width?: number;

  n_threads?: number;
  paragraph_number?: number;

  template_id?: string;
  caption_style?: string;
  color_preset?: string;
}

export interface TaskResponse {
  task_id: string;
}

export interface TaskQueryResponse {
  state: number;
  progress: number;
  videos?: string[];
  combined_videos?: string[];
  script?: string;
  terms?: string[];
  audio_file?: string;
  subtitle_path?: string;
}

export interface PluginInfo {
  name: string;
  display_name: string;
  version: string;
  description: string;
  author: string;
  plugin_type: string;
  enabled: boolean;
  active: boolean;
  available: boolean;
  builtin: boolean;
}
