'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authenticatedFetch } from '@/lib/api-client';
import type { Skill, SkillCreateBody, SkillUpdateBody } from '@/lib/interfaces/skill';

const SKILLS_KEY = ['skills'] as const;

async function fetchSkillsApi(): Promise<Skill[]> {
  const res = await authenticatedFetch('/api/ai/skills');
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || data.error || `Failed to load skills (${res.status})`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

export function useSkills() {
  const queryClient = useQueryClient();

  const {
    data: skills = [],
    isLoading,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: SKILLS_KEY,
    queryFn: fetchSkillsApi,
  });

  const error =
    queryError instanceof Error ? queryError.message : queryError ? String(queryError) : null;

  const createMutation = useMutation({
    mutationFn: async (body: SkillCreateBody): Promise<Skill> => {
      const res = await authenticatedFetch('/api/ai/skills', {
        method: 'POST',
        body: JSON.stringify({
          name: body.name,
          description: body.description ?? '',
          content: body.content ?? '',
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to create skill');
      }
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SKILLS_KEY }),
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, body }: { id: string; body: SkillUpdateBody }): Promise<Skill> => {
      const res = await authenticatedFetch(`/api/ai/skills/${id}`, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to update skill');
      }
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SKILLS_KEY }),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string): Promise<void> => {
      const res = await authenticatedFetch(`/api/ai/skills/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to delete skill');
      }
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SKILLS_KEY }),
  });

  const fetchSkills = async () => {
    await refetch();
  };
  const createSkill = (body: SkillCreateBody) => createMutation.mutateAsync(body);
  const updateSkill = (id: string, body: SkillUpdateBody) =>
    updateMutation.mutateAsync({ id, body });
  const deleteSkill = (id: string) => deleteMutation.mutateAsync(id);

  return { skills, isLoading, error, fetchSkills, createSkill, updateSkill, deleteSkill };
}
