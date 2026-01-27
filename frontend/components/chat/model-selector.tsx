'use client';

import { BrainCircuit, Loader2 } from 'lucide-react';
import Image from 'next/image';
import { memo, useState } from 'react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { DisplayModel } from '@/lib/interfaces/display-model';

type ModelSelectorProps = {
  modelId: string;
  models: DisplayModel[];
  onModelChange: (modelId: string) => void;
  isLoading: boolean;
  error: Error | null;
};

function ProviderIcon({ provider }: { provider?: string }) {
  const [error, setError] = useState(false);

  if (!provider || error) {
    return <BrainCircuit className="h-4 w-4 text-muted-foreground" />;
  }

  const iconPath = `/providers/${provider.toLowerCase()}.svg`;

  return (
    <Image
      src={iconPath}
      alt={provider}
      width={16}
      height={16}
      className="h-4 w-4 object-contain"
      onError={() => setError(true)}
    />
  );
}

export const ModelSelector = memo(function ModelSelector({
  modelId,
  models,
  onModelChange,
  isLoading,
  error,
}: ModelSelectorProps) {
  return (
    <Select
      value={modelId}
      onValueChange={onModelChange}
      disabled={isLoading || !!error || !models.length}
    >
      <SelectTrigger className="w-fit border-0 bg-transparent focus:ring-0 focus:ring-offset-0 focus:outline-none focus-visible:outline-none focus:border-0 focus-visible:border-0 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl font-medium text-xs pl-2 pr-1 shadow-none gap-1!">
        <div className="flex items-center gap-2 w-full">
          {isLoading ? (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              <span className="text-xs">Loading</span>
            </>
          ) : error ? (
            <span className="text-red-500 text-xs">Error</span>
          ) : !models.length ? (
            <span className="text-xs">No models</span>
          ) : (
            <SelectValue placeholder="Select model" />
          )}
        </div>
      </SelectTrigger>

      <SelectContent
        className="rounded-2xl border-0 shadow-border-medium bg-popover/95 backdrop-blur-sm animate-scale-in"
        align="start"
        sideOffset={4}
      >
        <SelectGroup>
          <SelectLabel className="text-xs text-muted-foreground px-2 py-1">Models</SelectLabel>
          {models.map((model) => (
            <SelectItem
              key={model.id}
              value={model.id}
              textValue={model.label}
              className="rounded-lg transition-colors duration-150 ease-out data-[state=checked]:font-medium text-xs"
            >
              <div className="flex items-center gap-2">
                <ProviderIcon provider={model.provider} />
                <span>{model.label}</span>
              </div>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
});
