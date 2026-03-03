import { useQuery } from '@tanstack/react-query';
import { authenticatedFetch } from '@/lib/api-client';
import type { DisplayPrompt } from '@/lib/interfaces/display-prompt';

interface PromptEntry {
  id: string;
  name: string;
  content: string;
}

async function fetchPrompts(): Promise<DisplayPrompt[]> {
  const response = await authenticatedFetch('/api/ai/prompts');
  if (!response.ok) {
    throw new Error('Failed to fetch prompts');
  }
  const data = await response.json();
  return data.prompts.map((prompt: PromptEntry) => ({
    id: prompt.id,
    label: prompt.name,
  }));
}

export function useAvailablePrompts() {
  const {
    data: prompts = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['available-prompts'],
    queryFn: fetchPrompts,
    staleTime: 5 * 60 * 1000,
  });

  return { prompts, isLoading, error };
}
