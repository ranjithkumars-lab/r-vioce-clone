import apiClient from './client';
import type { JobRecord, JobCreate } from '../types/job';

export const jobApi = {
  createJob: async (data: JobCreate): Promise<JobRecord> => {
    const payload = {
      voice_id: data.voice_id,
      text: data.script,
      engine: data.engine
    };
    const response = await apiClient.post<any>('/jobs/enqueue', payload);
    return {
      id: response.data.job_id,
      status: response.data.status,
      progress: response.data.progress_percentage,
      voice_id: data.voice_id,
      script: data.script,
      engine: data.engine,
      created_at: new Date().toISOString(),
      result_audio_path: response.data.output_url,
      error_message: response.data.error,
    } as JobRecord;
  },

  getJob: async (id: string): Promise<JobRecord> => {
    const response = await apiClient.get<any>(`/jobs/${id}`);
    return {
      id: response.data.job_id,
      status: response.data.status,
      progress: response.data.progress_percentage,
      result_audio_path: response.data.output_url,
      error_message: response.data.error,
      // The backend JobStatusResponse currently omits script/voice_id, so we cast to unknown
      voice_id: '',
      script: '',
      engine: '',
      created_at: new Date().toISOString(),
    } as unknown as JobRecord;
  },

  listJobs: async (limit: number = 50, skip: number = 0): Promise<JobRecord[]> => {
    const response = await apiClient.get<any[]>('/jobs', {
      params: { limit, skip }
    });
    return response.data.map(job => ({
      id: job.job_id,
      status: job.status,
      progress: job.progress_percentage,
      result_audio_path: job.output_url,
      error_message: job.error,
      voice_id: '',
      script: '',
      engine: '',
      created_at: new Date().toISOString(),
    })) as unknown as JobRecord[];
  },
  
  cancelJob: async (id: string): Promise<JobRecord> => {
    // The backend doesn't have a cancel endpoint right now, but for completeness:
    const response = await apiClient.post<any>(`/jobs/${id}/cancel`);
    return {
      id: response.data.job_id,
      status: response.data.status,
      progress: response.data.progress_percentage,
      voice_id: '',
      script: '',
      engine: '',
      created_at: new Date().toISOString(),
    } as unknown as JobRecord;
  },
};
