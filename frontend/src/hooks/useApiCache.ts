import { useEffect, useState, useRef, useCallback } from 'react';

/**
 * Simple in-memory cache with stale-while-revalidate semantics.
 * Navigating back to a page shows cached data instantly, then refreshes in background.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<unknown>>();

const STALE_MS = 30_000; // 30s — serve from cache, revalidate in background

export function clearCache(keyPrefix?: string) {
  if (!keyPrefix) {
    cache.clear();
    return;
  }
  for (const key of cache.keys()) {
    if (key.startsWith(keyPrefix)) cache.delete(key);
  }
}

export function useCachedFetch<T>(
  key: string | null,
  fetcher: () => Promise<T>,
) {
  const cached = key ? (cache.get(key) as CacheEntry<T> | undefined) : undefined;
  const [data, setData] = useState<T | null>(cached?.data ?? null);
  const [loading, setLoading] = useState(!cached);
  const [error, setError] = useState(false);
  const mountedRef = useRef(true);

  const refetch = useCallback(() => {
    if (!key) return;
    setLoading((prev) => !cache.has(key) ? true : prev);
    fetcher()
      .then((result) => {
        cache.set(key, { data: result, timestamp: Date.now() });
        if (mountedRef.current) {
          setData(result);
          setError(false);
        }
      })
      .catch(() => {
        if (mountedRef.current) setError(true);
      })
      .finally(() => {
        if (mountedRef.current) setLoading(false);
      });
  }, [key, fetcher]);

  useEffect(() => {
    mountedRef.current = true;
    if (!key) {
      setLoading(false);
      return;
    }

    const entry = cache.get(key) as CacheEntry<T> | undefined;
    if (entry) {
      setData(entry.data);
      setLoading(false);
      // Revalidate if stale
      if (Date.now() - entry.timestamp > STALE_MS) {
        refetch();
      }
    } else {
      refetch();
    }

    return () => { mountedRef.current = false; };
  }, [key, refetch]);

  return { data, loading, error, refetch };
}
