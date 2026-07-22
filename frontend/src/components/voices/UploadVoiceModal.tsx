import React, { useState, useRef, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { voiceApi } from '../../api/voiceApi';
import { useNotificationStore } from '../../stores/useNotificationStore';
import { X, UploadCloud, Info, Play, Pause, FileAudio } from 'lucide-react';
import './UploadVoiceModal.css';

interface UploadVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadVoiceModal({ isOpen, onClose }: UploadVoiceModalProps) {
  const [name, setName] = useState('');
  const [language, setLanguage] = useState('en');
  const [gender, setGender] = useState('unspecified');
  const [engine, setEngine] = useState('f5tts');
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  const mutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return voiceApi.uploadVoice(formData, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
    },
    onSuccess: () => {
      addNotification({ type: 'success', message: 'Voice cloned successfully!' });
      queryClient.invalidateQueries({ queryKey: ['voices'] });
      resetAndClose();
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Failed to upload voice.';
      addNotification({ type: 'error', message: msg });
      setUploadProgress(0); // reset progress on failure
    },
  });

  const resetAndClose = () => {
    setName('');
    setLanguage('en');
    setGender('unspecified');
    setEngine('f5tts');
    setFile(null);
    setUploadProgress(0);
    setIsPlaying(false);
    onClose();
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (mutation.isPending) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  }, [mutation.isPending]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile: File) => {
    const validExtensions = ['.wav', '.mp3', '.m4a', '.flac'];
    const hasValidExtension = validExtensions.some(ext => selectedFile.name.toLowerCase().endsWith(ext));
    if (!hasValidExtension) {
      addNotification({ type: 'error', message: `Only ${validExtensions.join(', ')} files are supported.` });
      return;
    }
    
    if (selectedFile.size > 30 * 1024 * 1024) {
      addNotification({ type: 'error', message: 'File is too large (max 30MB).' });
      return;
    }

    setFile(selectedFile);
    setIsPlaying(false);
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      addNotification({ type: 'error', message: 'Please provide a voice name.' });
      return;
    }
    if (!file) {
      addNotification({ type: 'error', message: 'Please upload a reference audio file.' });
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('language', language);
    formData.append('gender', gender);
    formData.append('engine', engine);
    formData.append('file', file);

    mutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay animate-fade-in" onClick={() => !mutation.isPending && resetAndClose()}>
      <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
        
        <header className="modal-header">
          <h2>Clone New Voice</h2>
          <button 
            className="btn-icon" 
            onClick={resetAndClose} 
            disabled={mutation.isPending}
            title="Close"
          >
            <X size={20} />
          </button>
        </header>

        <div className="modal-body">
          <form id="upload-voice-form" onSubmit={handleSubmit}>
            
            <div className="form-group">
              <label>Voice Name</label>
              <input 
                type="text" 
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. My Voice, John Doe"
                disabled={mutation.isPending}
                required
                maxLength={100}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Language</label>
                <select 
                  value={language} 
                  onChange={e => setLanguage(e.target.value)}
                  disabled={mutation.isPending}
                >
                  <option value="en">English (en)</option>
                  <option value="ta">Tamil (ta)</option>
                </select>
              </div>
              <div className="form-group">
                <label>Gender</label>
                <select 
                  value={gender} 
                  onChange={e => setGender(e.target.value)}
                  disabled={mutation.isPending}
                >
                  <option value="unspecified">Unspecified</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Engine</label>
                <select 
                  value={engine} 
                  onChange={e => setEngine(e.target.value)}
                  disabled={mutation.isPending}
                >
                  <option value="f5tts">F5-TTS</option>
                  <option value="mock">Mock Engine</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Reference Audio</label>
              <div 
                className={`dropzone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''} ${mutation.isPending ? 'disabled' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {!file ? (
                  <div className="dropzone-empty">
                    <UploadCloud size={32} className="text-muted" />
                    <p>Drag and drop your audio file here</p>
                    <span className="text-small text-muted">Supports .wav, .mp3, .m4a, .flac</span>
                    <label className="btn-secondary btn-small file-browse-btn">
                      Browse Files
                      <input 
                        type="file" 
                        accept=".wav,.mp3,.m4a,.flac" 
                        onChange={handleFileChange}
                        disabled={mutation.isPending}
                        hidden
                      />
                    </label>
                  </div>
                ) : (
                  <div className="dropzone-file">
                    <FileAudio size={32} className="text-accent" />
                    <div className="file-info">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                    </div>
                    <div className="file-actions">
                      <button 
                        type="button" 
                        className="btn-icon" 
                        onClick={togglePlayback}
                        disabled={mutation.isPending}
                      >
                        {isPlaying ? <Pause size={18} /> : <Play size={18} />}
                      </button>
                      <button 
                        type="button" 
                        className="btn-icon btn-remove" 
                        onClick={() => { setFile(null); setIsPlaying(false); }}
                        disabled={mutation.isPending}
                      >
                        <X size={18} />
                      </button>
                    </div>
                    <audio 
                      ref={audioRef} 
                      src={URL.createObjectURL(file)} 
                      onEnded={() => setIsPlaying(false)}
                      style={{ display: 'none' }}
                    />
                  </div>
                )}
              </div>
            </div>

            {mutation.isPending && (
              <div className="upload-progress-container">
                <div className="progress-header">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                </div>
              </div>
            )}

            <div className="info-panel">
              <div className="info-icon">
                <Info size={16} />
              </div>
              <div className="info-content">
                <strong>Voice Recording Tips</strong>
                <ul>
                  <li>Record in a quiet environment.</li>
                  <li>Speak naturally and clearly.</li>
                  <li>Provide 10-30 seconds of clear speech.</li>
                  <li>Avoid background noise or overlapping voices.</li>
                </ul>
              </div>
            </div>

          </form>
        </div>

        <footer className="modal-footer">
          <button 
            type="button" 
            className="btn-secondary" 
            onClick={resetAndClose}
            disabled={mutation.isPending}
          >
            Cancel
          </button>
          <button 
            type="submit" 
            form="upload-voice-form"
            className="btn-primary"
            disabled={mutation.isPending || !name || !file}
          >
            {mutation.isPending ? 'Uploading...' : 'Clone Voice'}
          </button>
        </footer>
      </div>
    </div>
  );
}
