import { useEffect, useRef, useState, useCallback } from 'react';
import type { WsStageEvent } from '@/types';

interface StageStatus {
  stage: string;
  status: 'in_progress' | 'complete' | 'failed';
  timestamp: string;
}

interface UseProcessingStreamReturn {
  statuses: Map<string, StageStatus>;
  isConnected: boolean;
  error: string | null;
}

export function useProcessingStream(jobId: string | null): UseProcessingStreamReturn {
  const [statuses, setStatuses] = useState<Map<string, StageStatus>>(new Map());
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const MAX_RETRIES = 3;

  const connect = useCallback(() => {
    if (!jobId) return;

    const token = localStorage.getItem('rax_token') || '';
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/pipeline/${jobId}?token=${token}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data: WsStageEvent = JSON.parse(event.data);
        setStatuses((prev) => {
          const next = new Map(prev);
          next.set(`${data.resume_id}:${data.stage}`, {
            stage: data.stage,
            status: data.status,
            timestamp: data.timestamp,
          });
          return next;
        });
      } catch {
        // Ignore non-JSON messages like pong
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      if (retriesRef.current < MAX_RETRIES) {
        retriesRef.current++;
        const delay = Math.min(1000 * 2 ** retriesRef.current, 8000);
        setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      setError('WebSocket connection error');
    };
  }, [jobId]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  return { statuses, isConnected, error };
}
