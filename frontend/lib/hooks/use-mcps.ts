'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authenticatedFetch } from '@/lib/api-client';
import type { Mcp, McpCreateBody, McpUpdateBody } from '@/lib/interfaces/mcp';

const MCPS_KEY = ['mcps'] as const;

async function fetchMcpsApi(): Promise<Mcp[]> {
  const res = await authenticatedFetch('/api/ai/mcps');
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || data.error || `Failed to load MCPs (${res.status})`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

export function useMcps() {
  const queryClient = useQueryClient();

  const {
    data: mcps = [],
    isLoading,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: MCPS_KEY,
    queryFn: fetchMcpsApi,
  });

  const error =
    queryError instanceof Error ? queryError.message : queryError ? String(queryError) : null;

  const createMutation = useMutation({
    mutationFn: async (body: McpCreateBody): Promise<Mcp> => {
      const res = await authenticatedFetch('/api/ai/mcps', {
        method: 'POST',
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to create MCP');
      }
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MCPS_KEY }),
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, body }: { id: string; body: McpUpdateBody }): Promise<Mcp> => {
      const res = await authenticatedFetch(`/api/ai/mcps/${id}`, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to update MCP');
      }
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MCPS_KEY }),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string): Promise<void> => {
      const res = await authenticatedFetch(`/api/ai/mcps/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to delete MCP');
      }
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MCPS_KEY }),
  });

  const checkMutation = useMutation({
    mutationFn: async (
      id: string
    ): Promise<{ status: string; tool_count: number; error?: string }> => {
      const res = await authenticatedFetch(`/api/ai/mcps/${id}/check`, { method: 'POST' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Check failed');
      }
      const data = await res.json();
      if (data.status === 'error') {
        throw new Error(data.error || 'MCP check failed');
      }
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MCPS_KEY }),
  });

  const fetchMcps = async () => {
    await refetch();
  };
  const createMcp = (body: McpCreateBody) => createMutation.mutateAsync(body);
  const updateMcp = (id: string, body: McpUpdateBody) => updateMutation.mutateAsync({ id, body });
  const deleteMcp = (id: string) => deleteMutation.mutateAsync(id);
  const checkMcp = (id: string) => checkMutation.mutateAsync(id);

  return { mcps, isLoading, error, fetchMcps, createMcp, updateMcp, deleteMcp, checkMcp };
}
