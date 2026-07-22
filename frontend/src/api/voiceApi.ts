import apiClient from './client';
import type { Voice, VoiceCreate } from '../types/voice';

export const voiceApi = {
  getVoices: async (): Promise<Voice[]> => {
    const response = await apiClient.get<{total: number, voices: Voice[]}>('/voices');
    return response.data.voices;
  },

  getVoice: async (id: string): Promise<Voice> => {
    const response = await apiClient.get<Voice>(`/voices/${id}`);
    return response.data;
  },

  createVoice: async (data: VoiceCreate): Promise<Voice> => {
    const response = await apiClient.post<Voice>('/voices', data);
    return response.data;
  },

  uploadVoice: async (data: FormData, onUploadProgress?: (progressEvent: any) => void): Promise<Voice> => {
    const response = await apiClient.post<{message: string, voice: Voice}>('/voices/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data.voice;
  },
};
