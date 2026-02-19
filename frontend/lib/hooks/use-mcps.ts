'use client';

import { useCallback, useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api-client';
import type { Mcp, McpCreateBody, McpUpdateBody } from '@/lib/interfaces/mcp';

export function useMcps() {
  const [mcps, setMcps] = useState<Mcp[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMcps = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authenticatedFetch('/api/mcps');
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || `Failed to load MCPs (${res.status})`);
      }
      const data = await res.json();
      setMcps(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load MCPs');
      setMcps([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMcps();
  }, [fetchMcps]);

  const createMcp = useCallback(async (body: McpCreateBody): Promise<Mcp | null> => {
    const res = await authenticatedFetch('/api/mcps', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || data.error || 'Failed to create MCP');
    }
    const created = await res.json();
    setMcps((prev) => [...prev, created]);
    return created;
  }, []);

  const updateMcp = useCallback(async (id: string, body: McpUpdateBody): Promise<Mcp | null> => {
    const res = await authenticatedFetch(`/api/mcps/${id}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || data.error || 'Failed to update MCP');
    }
    const updated = await res.json();
    setMcps((prev) => prev.map((m) => (m.id === id ? updated : m)));
    return updated;
  }, []);

  const deleteMcp = useCallback(async (id: string): Promise<void> => {
    const res = await authenticatedFetch(`/api/mcps/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || data.error || 'Failed to delete MCP');
    }
    setMcps((prev) => prev.filter((m) => m.id !== id));
  }, []);

  const checkMcp = useCallback(
    async (id: string): Promise<{ status: string; tool_count: number }> => {
      const res = await authenticatedFetch(`/api/mcps/${id}/check`, { method: 'POST' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Check failed');
      }
      const data = await res.json();
      setMcps((prev) =>
        prev.map((m) =>
          m.id === id
            ? {
                ...m,
                last_status: data.status,
                last_tool_count: data.tool_count,
                last_checked_at: new Date().toISOString(),
              }
            : m
        )
      );
      return { status: data.status, tool_count: data.tool_count };
    },
    []
  );

  return { mcps, loading, error, fetchMcps, createMcp, updateMcp, deleteMcp, checkMcp };
}
