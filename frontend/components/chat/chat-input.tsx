'use client';

import { ArrowUpIcon, PaperclipIcon } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { ModelSelector } from '@/components/chat/model-selector';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import type { DisplayModel } from '@/lib/display-model';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;

  // Model selection props
  models: DisplayModel[];
  modelId: string;
  onModelChange: (modelId: string) => void;
  isModelLoading: boolean;
  modelError: Error | null;
}

export function ChatInput({
  input,
  setInput,
  onSubmit,
  isLoading,
  models,
  modelId,
  onModelChange,
  isModelLoading,
  modelError,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto'; // Reset height to calculate scrollHeight
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`; // Cap at 200px
    }
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [adjustHeight]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <form onSubmit={onSubmit} className="w-full relative">
      <div className="relative flex flex-col w-full p-3 border rounded-2xl shadow-sm bg-background/80 backdrop-blur-sm focus-within:ring-1 focus-within:ring-ring transition-all">
        <Textarea
          ref={textareaRef}
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="min-h-15 w-full resize-none border-0 shadow-none bg-transparent focus-visible:ring-0 p-1 text-base"
          rows={1}
        />
        <div className="flex justify-between items-center mt-2">
          <div className="flex items-center gap-2">
            <ModelSelector
              modelId={modelId}
              models={models}
              onModelChange={onModelChange}
              isLoading={isModelLoading}
              error={modelError}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
            >
              <PaperclipIcon className="h-4 w-4" />
            </Button>
          </div>
          <Button
            type="submit"
            size="icon"
            className="h-8 w-8 rounded-full"
            disabled={!input.trim() || isLoading}
          >
            <ArrowUpIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </form>
  );
}
