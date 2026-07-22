export interface JobRecord {
  id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  voice_id: string;
  script: string;
  engine: string;
  result_audio_path?: string;
  error_message?: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface JobCreate {
  voice_id: string;
  script: string;
  engine: string;
}
