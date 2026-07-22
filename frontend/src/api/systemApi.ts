import apiClient from './client';
import type { HealthStatus } from '../types/system';

export const systemApi = {
  getHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },
};
