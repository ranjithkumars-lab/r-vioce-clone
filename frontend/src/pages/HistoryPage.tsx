import { useQuery } from '@tanstack/react-query';
import { jobApi } from '../api/jobApi';
import { Card } from '../components/common/Card';
import { AudioPlayer } from '../components/audio/AudioPlayer';
import { ListMusic, Clock, Settings } from 'lucide-react';
import { formatDate } from '../utils/formatDate';
import './HistoryPage.css';

export function HistoryPage() {
  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['history'],
    queryFn: () => jobApi.listJobs(100, 0),
  });

  // Filter only completed jobs that have a result audio path
  const completedJobs = jobs?.filter(job => job.status === 'COMPLETED' && job.result_audio_path) || [];

  return (
    <div className="history-page animate-fade-in">
      <header className="page-header">
        <div>
          <h1>Audio History</h1>
          <p>Your generated audio archive</p>
        </div>
      </header>

      {error && (
        <div className="alert error">
          Failed to load history. Please try again later.
        </div>
      )}

      {isLoading && (
        <div className="history-list">
          {[1, 2, 3].map(i => (
            <div key={i} className="glass-panel history-item skeleton">
              Loading...
            </div>
          ))}
        </div>
      )}

      {jobs && (
        <div className="history-list">
          {completedJobs.length === 0 ? (
            <div className="empty-state">
              <ListMusic size={48} className="text-muted" />
              <p>No generated audio found in your history.</p>
            </div>
          ) : (
            completedJobs.map(job => (
              <Card key={job.id} className="history-item">
                <div className="history-item-content">
                  <div className="history-meta">
                    <span className="badge-model">{job.engine}</span>
                    <div className="history-detail">
                      <Clock size={14} className="text-muted" />
                      <span className="text-muted text-small">{formatDate(job.created_at)}</span>
                    </div>
                  </div>
                  
                  <p className="history-script">
                    "{job.script}"
                  </p>

                  <div className="history-player-wrapper">
                    <AudioPlayer 
                      src={`http://localhost:8000/${job.result_audio_path}`} 
                      filename={`voice-studio-${job.id.substring(0, 8)}.wav`}
                    />
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
}
