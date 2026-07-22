import { create } from 'zustand';
import { JobRecord } from '../types/job';

interface JobStore {
  activeJobs: Record<string, JobRecord>;
  setJob: (job: JobRecord) => void;
  removeJob: (id: string) => void;
  updateJobProgress: (id: string, progress: number, status?: JobRecord['status']) => void;
  clearCompletedJobs: () => void;
}

export const useJobStore = create<JobStore>((set) => ({
  activeJobs: {},

  setJob: (job) => 
    set((state) => ({
      activeJobs: { ...state.activeJobs, [job.id]: job }
    })),

  removeJob: (id) =>
    set((state) => {
      const newJobs = { ...state.activeJobs };
      delete newJobs[id];
      return { activeJobs: newJobs };
    }),

  updateJobProgress: (id, progress, status) =>
    set((state) => {
      const job = state.activeJobs[id];
      if (!job) return state;
      return {
        activeJobs: {
          ...state.activeJobs,
          [id]: {
            ...job,
            progress,
            ...(status && { status })
          }
        }
      };
    }),

  clearCompletedJobs: () =>
    set((state) => {
      const newJobs = { ...state.activeJobs };
      Object.keys(newJobs).forEach(id => {
        if (newJobs[id].status === 'COMPLETED' || newJobs[id].status === 'FAILED') {
          delete newJobs[id];
        }
      });
      return { activeJobs: newJobs };
    })
}));
