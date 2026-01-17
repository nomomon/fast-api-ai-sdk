import { useEffect, useState } from 'react';
import type { DisplayModel } from '@/lib/display-model';

interface ModelEntry {
  id: string;
  name: string;
  provider: string;
}

export function useAvailableModels() {
  const [models, setModels] = useState<DisplayModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/models');
        if (!response.ok) {
          throw new Error('Failed to fetch models');
        }
        const data = await response.json();
        setModels(
          data.models.map((model: ModelEntry) => ({
            id: model.id,
            label: model.name,
            provider: model.provider,
          }))
        );
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch models'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchModels();
  }, []);

  return { models, isLoading, error };
}
