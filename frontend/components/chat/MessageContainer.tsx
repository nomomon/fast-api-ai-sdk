'use client';

import { MessageParts } from './MessageParts';
import { MessageSources } from './MessageSources';
import type { UIMessage, ChatStatus } from 'ai';

export interface MessageContainerProps {
  message: UIMessage;
  isLastMessage?: boolean;
  status?: ChatStatus;
  onRegenerate?: () => void;
}

export function MessageContainer({
  message,
  isLastMessage = false,
  status,
  onRegenerate,
}: MessageContainerProps) {
  if (!message.parts || message.parts.length === 0) {
    return null;
  }

  return (
    <div>
      {message.role === 'assistant' && (
        <MessageSources parts={message.parts} messageId={message.id} />
      )}
      <MessageParts
        parts={message.parts}
        messageId={message.id}
        role={message.role}
        isLastMessage={isLastMessage}
        status={status}
        onRegenerate={onRegenerate}
      />
    </div>
  );
}
