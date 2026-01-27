'use client';

import { Loader2 } from 'lucide-react';
import { memo } from 'react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { DisplayPrompt } from '@/lib/interfaces/display-prompt';

type PromptSelectorProps = {
  promptId: string;
  prompts: DisplayPrompt[];
  onPromptChange: (promptId: string) => void;
  isLoading: boolean;
  error: Error | null;
};

export const PromptSelector = memo(function PromptSelector({
  promptId,
  prompts,
  onPromptChange,
  isLoading,
  error,
}: PromptSelectorProps) {
  return (
    <Select
      value={promptId}
      onValueChange={onPromptChange}
      disabled={isLoading || !!error || !prompts.length}
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
          ) : !prompts.length ? (
            <span className="text-xs">No prompts</span>
          ) : (
            <SelectValue placeholder="Select prompt" />
          )}
        </div>
      </SelectTrigger>

      <SelectContent
        className="rounded-2xl border-0 shadow-border-medium bg-popover/95 backdrop-blur-sm animate-scale-in"
        align="start"
        sideOffset={4}
      >
        <SelectGroup>
          <SelectLabel className="text-xs text-muted-foreground px-2 py-1">Prompts</SelectLabel>
          {prompts.map((prompt) => (
            <SelectItem
              key={prompt.id}
              value={prompt.id}
              textValue={prompt.label}
              className="rounded-lg transition-colors duration-150 ease-out data-[state=checked]:font-medium text-xs"
            >
              <span>{prompt.label}</span>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
});
