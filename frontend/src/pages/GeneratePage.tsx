import { useForm } from 'react-hook-form';
import { useQuery, useMutation } from '@tanstack/react-query';
import { voiceApi } from '../api/voiceApi';
import { jobApi } from '../api/jobApi';
import { getErrorMessage } from '../api/client';
import type { JobCreate } from '../types/job';
import { useNotificationStore } from '../stores/useNotificationStore';
import { Card } from '../components/common/Card';
import { Mic2, Settings2, Play } from 'lucide-react';
import './GeneratePage.css';

export function GeneratePage() {
  const { addNotification } = useNotificationStore();
  
  const { data: voices, isLoading: loadingVoices } = useQuery({
    queryKey: ['voices'],
    queryFn: voiceApi.getVoices,
  });

  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<JobCreate>({
    defaultValues: {
      engine: 'mock',
    }
  });

  const mutation = useMutation({
    mutationFn: jobApi.createJob,
    onSuccess: () => {
      addNotification({ type: 'success', message: 'Job submitted successfully!' });
      reset({ script: '' });
      // In Step 2, this job will flow into the JobStore
    },
    onError: (err: any) => {
      addNotification({ 
        type: 'error', 
        message: getErrorMessage(err) 
      });
    },
  });

  const onSubmit = (data: JobCreate) => {
    mutation.mutate(data);
  };

  return (
    <div className="generate-page animate-fade-in">
      <header className="page-header">
        <div>
          <h1>Generate Audio</h1>
          <p>Text to speech synthesis</p>
        </div>
      </header>

      <div className="generate-content">
        <Card className="form-card">
          <form onSubmit={handleSubmit(onSubmit)} className="generation-form">
            
            <div className="form-group">
              <label>
                <Mic2 size={16} />
                Select Voice
              </label>
              <select 
                {...register('voice_id', { required: 'Please select a voice' })}
                disabled={loadingVoices}
                className={errors.voice_id ? 'input-error' : ''}
              >
                <option value="">-- Choose a Voice --</option>
                {/* Handle case where voices might be cached as {voices: []} from before the fix */}
                {((Array.isArray(voices) ? voices : (voices as any)?.voices) || []).filter((v: any) => v.status === 'ACTIVE').map((voice: any) => (
                  <option key={voice.id} value={voice.id}>
                    {voice.name} ({voice.engine})
                  </option>
                ))}
              </select>
              {errors.voice_id && <span className="error-text">{errors.voice_id.message}</span>}
            </div>

            <div className="form-group">
              <label>
                <Settings2 size={16} />
                Audio Engine
              </label>
              <select {...register('engine', { required: 'Engine is required' })}>
                <option value="mock">Mock Engine (Fast)</option>
                <option value="f5tts">F5-TTS (High Quality)</option>
              </select>
            </div>

            <div className="form-group script-group">
              <label>Script</label>
              <textarea 
                {...register('script', { 
                  required: 'Script is required',
                  minLength: { value: 5, message: 'Script is too short' },
                  maxLength: { value: 5000, message: 'Script is too long' }
                })}
                placeholder="Type your script here..."
                rows={8}
                className={errors.script ? 'input-error' : ''}
              />
              <div className="script-footer">
                {errors.script ? (
                  <span className="error-text">{errors.script.message}</span>
                ) : (
                  <span className="text-muted text-small">Max 5000 characters.</span>
                )}
              </div>
            </div>

            <div className="form-actions">
              <button 
                type="submit" 
                className="btn-primary btn-large"
                disabled={isSubmitting || mutation.isPending}
              >
                <Play size={20} />
                {mutation.isPending ? 'Submitting...' : 'Generate Audio'}
              </button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
