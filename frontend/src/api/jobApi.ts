import apiClient from './client';
import type { JobRecord, JobCreate } from '../types/job';

export const jobApi = {
  createJob: async (data: JobCreate): Promise<JobRecord> => {
    const response = await apiClient.post<JobRecord>('/jobs', data);
    return response.data;
  },

  getJob: async (id: string): Promise<JobRecord> => {
    const response = await apiClient.get<JobRecord>(`/jobs/${id}`);
    return response.data;
  },

  listJobs: async (limit: number = 50, skip: number = 0): Promise<JobRecord[]> => {
    const response = await apiClient.get<JobRecord[]>('/jobs', {
      params: { limit, skip }
    });
    return response.data;
  },
  
  cancelJob: async (id: string): Promise<JobRecord> => {
    const response = await apiClient.post<JobRecord>(`/jobs/${id}/cancel`);
    return response.data;
  },
};
