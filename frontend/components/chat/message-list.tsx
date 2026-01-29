'use client';

import type { UIMessage } from 'ai';
import { useCallback, useEffect, useRef } from 'react';
import { MessageItem } from './message-item';

interface MessageListProps {
  messages: UIMessage[];
  isLoading: boolean;
  onRegenerate: (messageId: string) => void;
  onEdit: (messageId: string, newText: string) => void;
}

export function MessageList({ messages, isLoading, onRegenerate, onEdit }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: ensure scroll on messages change
  useEffect(() => {
    // Scroll on mount and when messages change
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8 py-4 hide-scrollbar">
      <div className="flex flex-col gap-4 md:gap-6 pb-4 pt-10 md:pt-0">
        {messages.map((m, index) => (
          <MessageItem
            key={m.id}
            message={m}
            isStreaming={isLoading && index === messages.length - 1}
            onRegenerate={onRegenerate}
            onEdit={onEdit}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
