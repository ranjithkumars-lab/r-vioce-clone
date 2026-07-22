import { useEffect, useRef, useCallback } from 'react';
import { useJobStore } from '../stores/useJobStore';
import { useNotificationStore } from '../stores/useNotificationStore';

export function useJobEvents() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  
  const { setJob, updateJobProgress } = useJobStore();
  const { addNotification } = useNotificationStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    // Use dynamic relative WebSocket URL so it works regardless of the host IP
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/jobs`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      reconnectAttempts.current = 0;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle different event types from the backend EventBus
        if (data.type === 'JOB_CREATED' || data.type === 'JOB_UPDATED') {
          setJob(data.payload);
        } else if (data.type === 'JOB_PROGRESS') {
          updateJobProgress(data.payload.id, data.payload.progress, data.payload.status);
        } else if (data.type === 'JOB_FAILED') {
          updateJobProgress(data.payload.id, data.payload.progress, 'FAILED');
          addNotification({ 
            type: 'error', 
            message: `Job ${data.payload.id.substring(0,8)} failed: ${data.payload.error}` 
          });
        } else if (data.type === 'JOB_COMPLETED') {
          updateJobProgress(data.payload.id, 1.0, 'COMPLETED');
          addNotification({ 
            type: 'success', 
            message: `Audio generation completed!` 
          });
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.onclose = (event) => {
      if (!event.wasClean) {
        // Exponential backoff reconnect
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current += 1;
        
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, timeout);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      // Close will be called automatically, triggering reconnect
    };

    wsRef.current = ws;
  }, [setJob, updateJobProgress, addNotification]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        // Only close if it's actually open to avoid the "closed before established" warning in React StrictMode
        if (wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.close();
        }
      }
    };
  }, [connect]);
}
