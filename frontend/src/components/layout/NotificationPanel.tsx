import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useNotificationStore } from '../../stores/useNotificationStore';
import './NotificationPanel.css';

export function NotificationPanel() {
  const { notifications, removeNotification } = useNotificationStore();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="text-success" size={20} />;
      case 'error': return <AlertCircle className="text-error" size={20} />;
      case 'warning': return <AlertTriangle className="text-warning" size={20} />;
      default: return <Info className="text-accent" size={20} />;
    }
  };

  if (notifications.length === 0) return null;

  return (
    <div className="notification-panel">
      {notifications.map((notification) => (
        <div key={notification.id} className={`notification-toast glass-panel animate-slide-in`}>
          <div className="toast-icon">
            {getIcon(notification.type)}
          </div>
          <div className="toast-message">
            {notification.message}
          </div>
          <button 
            className="toast-close" 
            onClick={() => removeNotification(notification.id)}
          >
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}
