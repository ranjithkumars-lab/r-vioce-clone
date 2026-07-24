import { useEffect, useRef, useCallback } from 'react';
import { useJobStore } from '../stores/useJobStore';
import { useNotificationStore } from '../stores/useNotificationStore';

export function useJobEvents() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  
  const { setJob, updateJobProgress, updateJob } = useJobStore();
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
        if (data.event === 'ping') return;
        
        // Handle the backend's "job_update" event
        if (data.event === 'job_update' && data.data) {
          const payload = data.data;
          
          if (payload.status === 'COMPLETED') {
            // Ensure output_path is formatted as a relative URL if it's absolute
            let audioUrl = payload.output_path;
            if (audioUrl && audioUrl.includes('/workspace/backend/storage/generated/')) {
              audioUrl = `/api/v1/media/${audioUrl.split('/').pop()}`;
            }
            
            updateJob(payload.job_id, {
              status: 'COMPLETED',
              progress: 100,
              result_audio_path: audioUrl
            });
            addNotification({ 
              type: 'success', 
              message: `Audio generation completed!` 
            });
          } else if (payload.status === 'FAILED') {
            updateJob(payload.job_id, {
              status: 'FAILED',
              progress: 0,
              error_message: payload.error
            });
            addNotification({ 
              type: 'error', 
              message: `Job ${payload.job_id.substring(0,8)} failed: ${payload.error || 'Unknown error'}` 
            });
          } else {
            // Normal progress update
            updateJobProgress(payload.job_id, payload.progress, payload.status);
          }
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
