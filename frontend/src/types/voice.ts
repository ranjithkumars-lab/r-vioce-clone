export interface Voice {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  model_type: string;
  created_at: string;
  updated_at: string;
  reference_audio_path?: string;
  language?: string;
}

export interface VoiceCreate {
  name: string;
  description: string;
  model_type: string;
  language?: string;
}
