'use client';

import { Loader } from '@/components/ai-elements/loader';
import { MessageContainer } from './MessageContainer';
import type { UIMessage, ChatStatus } from 'ai';

export interface MessagesListProps {
  messages: UIMessage[];
  status?: ChatStatus;
  onRegenerate?: () => void;
}

export function MessagesList({ messages, status, onRegenerate }: MessagesListProps) {
  return (
    <>
      {messages.map((message, index) => {
        const isLastMessage = index === messages.length - 1;
        return (
          <MessageContainer
            key={message.id}
            message={message}
            isLastMessage={isLastMessage}
            status={status}
            onRegenerate={onRegenerate}
          />
        );
      })}
      {status === 'submitted' && <Loader />}
    </>
  );
}
