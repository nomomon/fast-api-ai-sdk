'use client';

import type { DynamicToolUIPart, UIMessage } from 'ai';
import { Streamdown } from 'streamdown';
import { Reasoning, ReasoningContent, ReasoningTrigger } from '@/components/ai-elements/reasoning';
import { ToolInvocation } from '@/components/chat/tool-invocation';
import { cn } from '@/lib/utils';

interface MessageItemProps {
  message: UIMessage;
  isStreaming: boolean;
}

export function MessageItem({ message, isStreaming }: MessageItemProps) {
  const isReasoning =
    message.role === 'assistant' && message.parts.some((part) => part.type === 'reasoning');

  return (
    <div
      className={cn({
        'bg-foreground text-background rounded-2xl p-3 md:p-4 ml-auto max-w-[90%] md:max-w-[75%] shadow-border-small font-medium text-sm md:text-base':
          message.role === 'user',
        'max-w-[95%] md:max-w-[85%] text-foreground/90 leading-relaxed text-sm md:text-base':
          message.role === 'assistant',
      })}
    >
      {/* Handle reasoning parts separately if they exist */}
      {isReasoning && (
        <Reasoning isStreaming={isStreaming}>
          <ReasoningTrigger />
          <ReasoningContent>
            {message.parts
              .filter((part) => part.type === 'reasoning')
              .map((part) => part.text || '')
              .join('')}
          </ReasoningContent>
        </Reasoning>
      )}

      {/* Handle text and other parts */}
      {message.parts.map((part, i) => {
        switch (part.type) {
          case 'text':
            return message.role === 'assistant' ? (
              <Streamdown key={`${message.id}-${i}`} isAnimating={isStreaming}>
                {part.text}
              </Streamdown>
            ) : (
              <div key={`${message.id}-${i}`}>{part.text}</div>
            );
          case 'reasoning':
            // Reasoning parts are handled above
            return null;
          default:
            if (part.type.startsWith('tool-')) {
              const toolPart = part as DynamicToolUIPart;
              return (
                <ToolInvocation
                  key={`${message.id}-${i}`}
                  toolType={toolPart.type}
                  toolName={toolPart.toolName}
                  state={toolPart.state}
                  input={toolPart.input}
                />
              );
            }
            return null;
        }
      })}
    </div>
  );
}
