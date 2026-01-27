import { useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api-client';
import type { DisplayPrompt } from '@/lib/interfaces/display-prompt';

interface PromptEntry {
  id: string;
  name: string;
  content: string;
}

export function useAvailablePrompts() {
  const [prompts, setPrompts] = useState<DisplayPrompt[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const response = await authenticatedFetch('/api/prompts');
        if (!response.ok) {
          throw new Error('Failed to fetch prompts');
        }
        const data = await response.json();
        setPrompts(
          data.prompts.map((prompt: PromptEntry) => ({
            id: prompt.id,
            label: prompt.name,
          }))
        );
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch prompts'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrompts();
  }, []);

  return { prompts, isLoading, error };
}
