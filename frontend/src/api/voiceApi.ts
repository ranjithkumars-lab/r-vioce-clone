import apiClient from './client';
import type { Voice, VoiceCreate } from '../types/voice';

export const voiceApi = {
  getVoices: async (): Promise<Voice[]> => {
    const response = await apiClient.get<Voice[]>('/voices');
    return response.data;
  },

  getVoice: async (id: string): Promise<Voice> => {
    const response = await apiClient.get<Voice>(`/voices/${id}`);
    return response.data;
  },

  createVoice: async (data: VoiceCreate): Promise<Voice> => {
    const response = await apiClient.post<Voice>('/voices', data);
    return response.data;
  },
};
