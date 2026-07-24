export interface Voice {
  id: string;
  name: string;
  language: string;
  gender: string;
  engine: string;
  status: string;
  duration: number;
  sample_rate: number;
  channels: number;
  file_path: string;
  created_at: string;
  updated_at: string;
  transcript_source?: string;
  reference_text?: string;
}

export interface VoiceCreate {
  name: string;
  language?: string;
  gender?: string;
  engine?: string;
}
