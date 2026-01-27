'use client';

import { ArrowUpIcon, PaperclipIcon } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  children?: React.ReactNode;
}

export function ChatInput({ input, setInput, onSubmit, isLoading, children }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto'; // Reset height to calculate scrollHeight
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`; // Cap at 200px
    }
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: ensure height adjustment on input change
  useEffect(() => {
    adjustHeight();
  }, [adjustHeight, input]);

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
          <div className="flex items-center gap-1">
            {children}
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              aria-label="Attach file"
            >
              <PaperclipIcon className="h-4 w-4" />
            </Button>
          </div>
          <Button
            type="submit"
            size="icon"
            className="h-8 w-8 rounded-full"
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
          >
            <ArrowUpIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </form>
  );
}
