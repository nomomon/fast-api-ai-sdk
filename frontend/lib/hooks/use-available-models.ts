import { useQuery } from '@tanstack/react-query';
import { authenticatedFetch } from '@/lib/api-client';
import type { DisplayModel } from '@/lib/interfaces/display-model';

interface ModelEntry {
  id: string;
  name: string;
  provider: string;
}

async function fetchModels(): Promise<DisplayModel[]> {
  const response = await authenticatedFetch('/api/ai/models');
  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }
  const data = await response.json();
  return data.models.map((model: ModelEntry) => ({
    id: model.id,
    label: model.name,
    provider: model.provider,
  }));
}

export function useAvailableModels() {
  const {
    data: models = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['available-models'],
    queryFn: fetchModels,
    staleTime: 5 * 60 * 1000,
  });

  return { models, isLoading, error };
}
