import { useEffect, useState } from 'react';
import { useAvailableModels } from '@/lib/hooks/use-available-models';

export function useDefaultModel() {
  const { models, isLoading, error } = useAvailableModels();
  const [modelId, setModelId] = useState<string>('');

  useEffect(() => {
    // if the request is still loading, do nothing
    if (isLoading || !models || models.length === 0) return;

    // if modelId is already set, do nothing (preserve user selection)
    if (modelId) return;

    const savedModelId = localStorage.getItem('default-model');

    if (savedModelId && models.some((m) => m.id === savedModelId)) {
      setModelId(savedModelId);
    } else {
      setModelId(models[0].id);
    }
  }, [models, isLoading, modelId]);

  const handleModelChange = (id: string) => {
    setModelId(id);
    localStorage.setItem('default-model', id);
  };

  return { modelId, setModelId: handleModelChange, models, isLoading, error };
}
