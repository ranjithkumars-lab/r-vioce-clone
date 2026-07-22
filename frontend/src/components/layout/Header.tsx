import { Bell } from 'lucide-react';
import './Header.css';

export function Header() {
  return (
    <header className="header glass-panel">
      <div className="header-breadcrumbs">
        {/* We can make this dynamic later based on route */}
        <span>Dashboard</span>
      </div>
      <div className="header-actions">
        <button className="icon-btn">
          <Bell size={20} />
          <span className="badge indicator-pulse"></span>
        </button>
        <div className="user-avatar">
          Admin
        </div>
      </div>
    </header>
  );
}
