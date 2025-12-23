'use client';

import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn('flex w-full mb-4', isUser ? 'justify-end' : 'justify-start')}>
      <Card
        className={cn('max-w-[80%]', isUser ? 'bg-primary text-primary-foreground' : 'bg-muted')}
      >
        <CardContent className="p-4">
          <div className="text-sm whitespace-pre-wrap break-words">{content}</div>
        </CardContent>
      </Card>
    </div>
  );
}
