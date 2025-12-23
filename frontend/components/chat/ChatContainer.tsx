'use client';

import { useCallback, useEffect, useRef } from 'react';
import { ChatInput, type ChatInputProps } from './ChatInput';
import { ChatMessage, type ChatMessageProps } from './ChatMessage';

export interface ChatContainerProps {
  messages: ChatMessageProps[];
  onSendMessage: ChatInputProps['onSendMessage'];
  isLoading?: boolean;
}

export function ChatContainer({ messages, onSendMessage, isLoading = false }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: We want to scroll when messages or loading state changes
  useEffect(() => {
    scrollToBottom();
  }, [messages.length, isLoading, scrollToBottom]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>Start a conversation by sending a message</p>
          </div>
        )}
        {messages.map((message, index) => (
          <ChatMessage
            key={`${message.role}-${index}-${message.content.slice(0, 10)}`}
            {...message}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg p-4">
              <div className="flex space-x-1">
                <div
                  className="w-2 h-2 bg-foreground rounded-full animate-bounce"
                  style={{ animationDelay: '0ms' }}
                />
                <div
                  className="w-2 h-2 bg-foreground rounded-full animate-bounce"
                  style={{ animationDelay: '150ms' }}
                />
                <div
                  className="w-2 h-2 bg-foreground rounded-full animate-bounce"
                  style={{ animationDelay: '300ms' }}
                />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t p-4">
        <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
