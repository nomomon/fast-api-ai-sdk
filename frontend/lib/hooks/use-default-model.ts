import { useEffect } from 'react';
import type { DisplayModel } from '@/lib/display-model';

interface UseDefaultModelOptions {
  modelId: string;
  models: DisplayModel[] | undefined;
  isLoading: boolean;
  error: Error | null;
  onModelChange: (modelId: string) => void;
}

export function useDefaultModel({
  modelId,
  models,
  isLoading,
  error,
  onModelChange,
}: UseDefaultModelOptions) {
  // Auto-select the first model if no modelId is provided or if the provided modelId is not valid
  useEffect(() => {
    if (!isLoading && !error && models && models.length > 0) {
      // Check if the current modelId is valid
      const isValidModelId = modelId && models.some((model) => model.id === modelId);

      // If no valid modelId is provided, select the first model
      if (!isValidModelId) {
        onModelChange(models[0].id);
      }
    }
  }, [models, modelId, onModelChange, isLoading, error]);

  // Get the effective modelId (either the provided one or the first available model)
  const effectiveModelId =
    modelId && models?.some((model) => model.id === modelId) ? modelId : models?.[0]?.id || '';

  return effectiveModelId;
}
