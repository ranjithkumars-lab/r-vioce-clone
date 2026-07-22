import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Mic2, ListMusic, Activity, Settings } from 'lucide-react';
import './Sidebar.css';

export function Sidebar() {
  const navItems = [
    { to: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/generate', icon: <Mic2 size={20} />, label: 'Generate' },
    { to: '/history', icon: <ListMusic size={20} />, label: 'History' },
    { to: '/voices', icon: <Mic2 size={20} />, label: 'Voices' },
    { to: '/system', icon: <Activity size={20} />, label: 'System' },
    { to: '/settings', icon: <Settings size={20} />, label: 'Settings' },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="logo-placeholder"></div>
        <h2>Voice Studio</h2>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.to} 
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
