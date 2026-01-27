'use client';

import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface SuggestionCardProps {
  summary: string;
  prompt: string;
  onClick: (prompt: string) => void;
}

export function SuggestionCard({ summary, prompt, onClick }: SuggestionCardProps) {
  return (
    <Card
      onClick={() => onClick(prompt)}
      className={cn(
        'cursor-pointer transition-all duration-150 ease-out',
        'hover:shadow-border-medium hover:scale-[1.02]',
        'bg-background/80 backdrop-blur-sm border',
        'shadow-border-small py-2.5'
      )}
    >
      <CardContent className="px-2">
        <p className="text-sm text-foreground font-medium">{summary}</p>
      </CardContent>
    </Card>
  );
}
