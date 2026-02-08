'use client';

import { cn } from '@/lib/utils';

interface SuggestionCardProps {
  summary: string;
  prompt: string;
  onClick: (prompt: string) => void;
}

export function SuggestionCard({ summary, prompt, onClick }: SuggestionCardProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(prompt)}
      className={cn(
        'w-full text-left cursor-pointer transition-all duration-150 ease-out',
        'hover:shadow-border-medium hover:scale-[1.02]',
        'bg-background/80 backdrop-blur-sm border rounded-xl',
        'shadow-border-small py-2.5 px-2',
        'flex flex-col gap-6',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
      )}
    >
      <span className="text-sm text-foreground font-medium">{summary}</span>
    </button>
  );
}
