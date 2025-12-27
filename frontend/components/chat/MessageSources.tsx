'use client';

import { Source, Sources, SourcesContent, SourcesTrigger } from '@/components/ai-elements/sources';
import type { UIPart } from 'ai';

export interface MessageSourcesProps {
  parts: UIPart[];
  messageId: string;
}

export function MessageSources({ parts, messageId }: MessageSourcesProps) {
  const sourceParts = parts.filter((part) => part.type === 'source-url');

  if (sourceParts.length === 0) {
    return null;
  }

  return (
    <Sources>
      <SourcesTrigger count={sourceParts.length} />
      {sourceParts.map((part, i) => (
        <SourcesContent key={`${messageId}-${i}`}>
          <Source key={`${messageId}-${i}`} href={part.url || ''} title={part.url} />
        </SourcesContent>
      ))}
    </Sources>
  );
}
