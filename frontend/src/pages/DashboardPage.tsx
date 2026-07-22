import { ActiveJobsPanel } from '../components/jobs/ActiveJobsPanel';
import { Card } from '../components/common/Card';
import { Mic2, PlayCircle, ListMusic } from 'lucide-react';
import { Link } from 'react-router-dom';
import './DashboardPage.css';

export function DashboardPage() {
  return (
    <div className="dashboard-page animate-fade-in">
      <header className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome back to Voice Studio</p>
      </header>

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <div className="quick-actions">
            <Link to="/generate" className="quick-action-card glass-panel">
              <PlayCircle className="text-accent" size={32} />
              <h3>Generate Audio</h3>
              <p>Create new speech from text</p>
            </Link>
            
            <Link to="/voices" className="quick-action-card glass-panel">
              <Mic2 className="text-success" size={32} />
              <h3>Voice Library</h3>
              <p>Manage your custom voice models</p>
            </Link>
            
            <Link to="/history" className="quick-action-card glass-panel">
              <ListMusic className="text-warning" size={32} />
              <h3>Audio History</h3>
              <p>Browse previously generated files</p>
            </Link>
          </div>

          <div className="recent-activity">
            {/* We will add recent history list here later in Step 5 */}
            <Card className="p-xl">
              <h3>Recent Generations</h3>
              <p className="text-muted mt-md">Check the History tab for your complete audio archive.</p>
            </Card>
          </div>
        </div>

        <aside className="dashboard-sidebar">
          <ActiveJobsPanel />
        </aside>
      </div>
    </div>
  );
}
