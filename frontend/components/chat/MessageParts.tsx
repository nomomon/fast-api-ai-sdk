'use client';

import {
  Message,
  MessageContent,
  MessageResponse,
  MessageActions,
  MessageAction,
} from '@/components/ai-elements/message';
import { Reasoning, ReasoningContent, ReasoningTrigger } from '@/components/ai-elements/reasoning';
import { CopyIcon, RefreshCcwIcon } from 'lucide-react';
import type { UIPart, ChatStatus } from 'ai';

export interface MessagePartsProps {
  parts: UIPart[];
  messageId: string;
  role: 'user' | 'assistant' | 'system';
  isLastMessage?: boolean;
  status?: ChatStatus;
  onRegenerate?: () => void;
}

export function MessageParts({
  parts,
  messageId,
  role,
  isLastMessage = false,
  status,
  onRegenerate,
}: MessagePartsProps) {
  return (
    <>
      {parts.map((part, i) => {
        switch (part.type) {
          case 'text':
            return (
              <Message key={`${messageId}-${i}`} from={role}>
                <MessageContent>
                  <MessageResponse>{part.text}</MessageResponse>
                </MessageContent>
                {role === 'assistant' && isLastMessage && i === parts.length - 1 && (
                  <MessageActions>
                    <MessageAction onClick={() => onRegenerate?.()} label="Retry">
                      <RefreshCcwIcon className="size-3" />
                    </MessageAction>
                    <MessageAction
                      onClick={() => navigator.clipboard.writeText(part.text || '')}
                      label="Copy"
                    >
                      <CopyIcon className="size-3" />
                    </MessageAction>
                  </MessageActions>
                )}
              </Message>
            );
          case 'reasoning':
            return (
              <Reasoning
                key={`${messageId}-${i}`}
                className="w-full"
                isStreaming={status === 'streaming' && i === parts.length - 1 && isLastMessage}
              >
                <ReasoningTrigger />
                <ReasoningContent>{part.text}</ReasoningContent>
              </Reasoning>
            );
          default:
            return null;
        }
      })}
    </>
  );
}
