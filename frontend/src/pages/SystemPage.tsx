import { useQuery } from '@tanstack/react-query';
import { systemApi } from '../api/systemApi';
import { Activity, Server, Clock } from 'lucide-react';
import './SystemPage.css';

export function SystemPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: systemApi.getHealth,
    refetchInterval: 10000, // Auto refresh every 10s
  });

  return (
    <div className="system-page animate-fade-in">
      <header className="page-header">
        <h1>System Health</h1>
        <p>Monitor backend services and worker status</p>
      </header>

      {error && (
        <div className="alert error">
          Failed to fetch system health. Is the backend running?
        </div>
      )}

      {isLoading && (
        <div className="glass-panel stat-card skeleton">
          Loading system metrics...
        </div>
      )}

      {data && (
        <div className="stats-grid">
          <div className="glass-panel stat-card">
            <div className="stat-header">
              <Activity className="text-accent" />
              <h3>Status</h3>
            </div>
            <div className="stat-value">
              <span className={`status-badge ${data.status === 'healthy' ? 'success' : 'error'}`}>
                {data.status.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="glass-panel stat-card">
            <div className="stat-header">
              <Server className="text-accent" />
              <h3>API Version</h3>
            </div>
            <div className="stat-value">{data.version}</div>
          </div>

          <div className="glass-panel stat-card">
            <div className="stat-header">
              <Clock className="text-accent" />
              <h3>Uptime</h3>
            </div>
            <div className="stat-value">
              {Math.floor(data.uptime / 60)}m {Math.floor(data.uptime % 60)}s
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
