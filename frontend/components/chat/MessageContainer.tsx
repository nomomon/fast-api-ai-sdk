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
  // During streaming, assistant messages might not have parts yet
  // Show them anyway if they're the last message and streaming
  const isStreaming = status === 'streaming' && isLastMessage && message.role === 'assistant';

  if (!message.parts || message.parts.length === 0) {
    // Show a placeholder for streaming messages without parts yet
    if (isStreaming) {
      return (
        <div>
          <MessageParts
            parts={[{ type: 'text', text: '' }]}
            messageId={message.id}
            role={message.role}
            isLastMessage={isLastMessage}
            status={status}
            onRegenerate={onRegenerate}
          />
        </div>
      );
    }
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
