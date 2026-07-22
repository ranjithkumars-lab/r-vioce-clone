import React from 'react';
import { useJobStore } from '../../stores/useJobStore';
import { Card } from '../common/Card';
import { Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { formatDuration } from '../../utils/formatDuration';
import './ActiveJobsPanel.css';

export function ActiveJobsPanel() {
  const { activeJobs, clearCompletedJobs } = useJobStore();
  const jobs = Object.values(activeJobs).sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  if (jobs.length === 0) return null;

  return (
    <div className="active-jobs-panel animate-fade-in">
      <div className="panel-header">
        <h3>Active Tasks</h3>
        <button className="btn-text" onClick={clearCompletedJobs}>
          Clear Completed
        </button>
      </div>

      <div className="jobs-list">
        {jobs.map(job => {
          const isCompleted = job.status === 'COMPLETED';
          const isFailed = job.status === 'FAILED';
          const isRunning = job.status === 'RUNNING';
          const isPending = job.status === 'PENDING';

          return (
            <Card key={job.id} className="job-card">
              <div className="job-info">
                <div className="job-status-icon">
                  {isRunning || isPending ? (
                    <Loader2 className="icon-spin text-accent" size={20} />
                  ) : isCompleted ? (
                    <CheckCircle className="text-success" size={20} />
                  ) : isFailed ? (
                    <XCircle className="text-error" size={20} />
                  ) : (
                    <AlertCircle className="text-warning" size={20} />
                  )}
                </div>
                <div className="job-details">
                  <div className="job-header">
                    <span className="job-id">Job {job.id.substring(0, 8)}</span>
                    <span className={`badge-status ${job.status.toLowerCase()}`}>
                      {job.status}
                    </span>
                  </div>
                  <div className="job-meta">
                    <span className="badge-model">{job.engine}</span>
                    <span className="text-muted text-small">
                      {job.script.substring(0, 40)}{job.script.length > 40 ? '...' : ''}
                    </span>
                  </div>
                </div>
              </div>

              {/* Progress Bar for active jobs */}
              {(isRunning || isPending) && (
                <div className="progress-container">
                  <div className="progress-bar-bg">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${job.progress * 100}%` }}
                    ></div>
                  </div>
                  <div className="progress-stats">
                    <span>{Math.round(job.progress * 100)}%</span>
                    {job.started_at && (
                      <span>
                        {formatDuration(
                          (new Date().getTime() - new Date(job.started_at).getTime()) / 1000
                        )}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
