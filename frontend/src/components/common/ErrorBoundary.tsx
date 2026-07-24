import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertOctagon } from 'lucide-react';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="glass-panel error-container">
            <AlertOctagon size={48} className="error-icon" />
            <h2>Something went wrong</h2>
            <p className="error-message">{this.state.error?.message}</p>
            <button 
              className="btn-primary" 
              onClick={() => window.location.href = '/'}
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
