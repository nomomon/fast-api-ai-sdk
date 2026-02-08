'use client';

import { type DataUIPart, type DynamicToolUIPart, isDataUIPart } from 'ai';
import { useState } from 'react';
import { Streamdown } from 'streamdown';
import { Reasoning, ReasoningContent, ReasoningTrigger } from '@/components/ai-elements/reasoning';
import { AgentMessageActions } from '@/components/chat/message-actions-agent';
import { UserMessageActions } from '@/components/chat/message-actions-user';
import { ToolInvocation } from '@/components/chat/tool-invocation';
import { getMessageMarkdown, getUserMessageText } from '@/components/chat/utils';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import type { ChatDataParts, ChatMessage } from '@/types/chat';
import { WorkflowPart } from './workflow-part';

interface MessageItemProps {
  message: ChatMessage;
  isStreaming: boolean;
  onRegenerate: (messageId: string) => void;
  onEdit: (messageId: string, newText: string) => void;
}

function UserMessageItem({ message, onEdit }: MessageItemProps) {
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState('');

  const handleStartEdit = () => {
    setEditDraft(getUserMessageText(message));
    setEditingMessageId(message.id);
  };

  const handleSaveEdit = () => {
    if (editDraft.trim()) {
      onEdit(message.id, editDraft.trim());
    }
    setEditingMessageId(null);
    setEditDraft('');
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditDraft('');
  };

  const isEditing = editingMessageId === message.id;

  return (
    <div className="flex items-end gap-2 ml-auto max-w-[95%] md:max-w-[85%] group">
      <UserMessageActions onEditClick={handleStartEdit} />
      {isEditing ? (
        <div className="flex flex-col gap-2 flex-1 min-w-0">
          <Textarea
            value={editDraft}
            onChange={(e) => setEditDraft(e.target.value)}
            className="min-h-20 resize-none"
            autoFocus
            aria-label="Edit message"
          />
          <div className="flex gap-2 justify-end">
            <Button variant="outline" size="sm" onClick={handleCancelEdit}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleSaveEdit} disabled={!editDraft.trim()}>
              Save
            </Button>
          </div>
        </div>
      ) : (
        <div
          className={cn(
            'bg-foreground text-background rounded-sm md:rounded-md p-2 md:px-3 shadow-border-small font-medium text-sm md:text-base'
          )}
        >
          {message.parts
            .filter((part) => part.type === 'text')
            .map((part, i) => (
              <div key={`${message.id}-${i}`}>{part.text}</div>
            ))}
        </div>
      )}
    </div>
  );
}

function AssistantMessageItem({ message, isStreaming, onRegenerate }: MessageItemProps) {
  const isReasoning = message.parts.some((part) => part.type === 'reasoning');
  const isWorkflow = message.parts.some((part) => isDataUIPart(part));

  return (
    <div className="max-w-[95%] md:max-w-[85%]">
      <div className="text-foreground/90 leading-relaxed text-sm md:text-base">
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

        {isWorkflow && (
          <WorkflowPart
            isStreaming={isStreaming}
            parts={message.parts.filter((part): part is DataUIPart<ChatDataParts> =>
              isDataUIPart(part)
            )}
          />
        )}

        {message.parts.map((part, i) => {
          switch (part.type) {
            case 'text':
              return (
                <Streamdown key={`${message.id}-${i}`} isAnimating={isStreaming}>
                  {part.text}
                </Streamdown>
              );
            case 'reasoning':
              return null;
            default:
              if (part.type.startsWith('tool-')) {
                const toolPart = part as DynamicToolUIPart;
                return (
                  <ToolInvocation
                    key={`${message.id}-${i}`}
                    toolType={toolPart.type}
                    state={toolPart.state}
                    input={toolPart.input}
                  />
                );
              }
              return null;
          }
        })}
      </div>
      <AgentMessageActions
        onRegenerate={() => onRegenerate(message.id)}
        onCopy={() => {
          navigator.clipboard.writeText(getMessageMarkdown(message));
        }}
        isStreaming={isStreaming}
      />
    </div>
  );
}

export function MessageItem(props: MessageItemProps) {
  if (props.message.role === 'user') {
    return <UserMessageItem {...props} />;
  } else if (props.message.role === 'assistant') {
    return <AssistantMessageItem {...props} />;
  }
  return null;
}
