import { useCallback, useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api-client';
import type { UserSkill, UserSkillUpdateRequest } from '@/lib/interfaces/user-skill';

interface UserSkillListResponse {
  skills: UserSkill[];
}

export function useUserSkills() {
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refetch = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    try {
      const response = await authenticatedFetch('/api/skills');
      if (!response.ok) {
        throw new Error('Failed to fetch skills');
      }
      const data: UserSkillListResponse = await response.json();
      setSkills(data.skills);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch skills'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { skills, isLoading, error, refetch };
}

export async function updateSkill(id: string, body: UserSkillUpdateRequest): Promise<UserSkill> {
  const response = await authenticatedFetch(`/api/skills/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ?? 'Failed to update skill');
  }
  return response.json();
}

export async function deleteSkill(id: string): Promise<void> {
  const response = await authenticatedFetch(`/api/skills/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ?? 'Failed to delete skill');
  }
}
