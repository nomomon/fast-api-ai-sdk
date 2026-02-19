'use client';

import { useCallback, useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api-client';
import type { Skill, SkillCreateBody, SkillUpdateBody } from '@/lib/interfaces/skill';

export function useSkills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authenticatedFetch('/api/skills');
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || `Failed to load skills (${res.status})`);
      }
      const data = await res.json();
      setSkills(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load skills');
      setSkills([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const createSkill = useCallback(async (body: SkillCreateBody): Promise<Skill | null> => {
    const res = await authenticatedFetch('/api/skills', {
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
    const created = await res.json();
    setSkills((prev) => [...prev, created]);
    return created;
  }, []);

  const updateSkill = useCallback(
    async (id: string, body: SkillUpdateBody): Promise<Skill | null> => {
      const res = await authenticatedFetch(`/api/skills/${id}`, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.error || 'Failed to update skill');
      }
      const updated = await res.json();
      setSkills((prev) => prev.map((s) => (s.id === id ? updated : s)));
      return updated;
    },
    []
  );

  const deleteSkill = useCallback(async (id: string): Promise<void> => {
    const res = await authenticatedFetch(`/api/skills/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || data.error || 'Failed to delete skill');
    }
    setSkills((prev) => prev.filter((s) => s.id !== id));
  }, []);

  return { skills, loading, error, fetchSkills, createSkill, updateSkill, deleteSkill };
}
