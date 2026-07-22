import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { voiceApi } from '../api/voiceApi';
import { Mic2, Plus } from 'lucide-react';
import { UploadVoiceModal } from '../components/voices/UploadVoiceModal';
import './VoiceListPage.css';

export function VoiceListPage() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const { data: voices, isLoading, error } = useQuery({
    queryKey: ['voices'],
    queryFn: voiceApi.getVoices,
  });

  return (
    <div className="voice-list-page animate-fade-in">
      <header className="page-header">
        <div>
          <h1>Voice Library</h1>
          <p>Manage and create custom voice models</p>
        </div>
        <button className="btn-primary" onClick={() => setIsUploadModalOpen(true)}>
          <Plus size={20} />
          Add Voice
        </button>
      </header>

      {error && (
        <div className="alert error">
          Failed to load voices. Please try again later.
        </div>
      )}

      {isLoading && (
        <div className="voices-grid">
          {[1, 2, 3].map(i => (
            <div key={i} className="glass-panel voice-card skeleton">
              Loading voice...
            </div>
          ))}
        </div>
      )}

      {voices && (
        <div className="voices-grid">
          {voices.length === 0 ? (
            <div className="empty-state">
              <Mic2 size={48} className="text-muted" />
              <p>No voices found in your library.</p>
            </div>
          ) : (
            voices.map(voice => (
              <div key={voice.id} className="glass-panel voice-card group">
                <div className="voice-card-header">
                  <h3>{voice.name}</h3>
                  <span className={`status-dot ${voice.status === 'READY' || voice.status === 'ACTIVE' ? 'active' : voice.status === 'PROCESSING' ? 'processing' : 'inactive'}`} title={`Status: ${voice.status}`}></span>
                </div>
                <p className="voice-description">
                  {voice.gender !== 'unspecified' ? voice.gender : 'Voice Profile'} • {voice.language} • {voice.duration.toFixed(1)}s
                </p>
                <div className="voice-card-footer">
                  <span className="badge-model">{voice.engine}</span>
                  {voice.transcript_source && (
                    <span className="badge-model" style={{marginLeft: '4px', backgroundColor: 'rgba(59, 130, 246, 0.2)'}}>
                      {voice.transcript_source === 'whisper' ? 'Auto-STT' : 'Manual'}
                    </span>
                  )}
                  <span className="text-muted text-small">
                    {new Date(voice.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <UploadVoiceModal 
        isOpen={isUploadModalOpen} 
        onClose={() => setIsUploadModalOpen(false)} 
      />
    </div>
  );
}
