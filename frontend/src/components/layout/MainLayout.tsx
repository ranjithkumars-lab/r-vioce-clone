import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { NotificationPanel } from './NotificationPanel';
import { useJobEvents } from '../../hooks/useJobEvents';
import './MainLayout.css';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  // Initialize global WebSocket connection for jobs
  useJobEvents();

  return (
    <div className="layout-container">
      <Sidebar />
      <div className="layout-content">
        <Header />
        <main className="layout-main">
          {children}
        </main>
      </div>
      <NotificationPanel />
    </div>
  );
}
