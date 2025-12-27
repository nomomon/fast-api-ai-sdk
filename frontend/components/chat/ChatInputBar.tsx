'use client';

import {
  PromptInput,
  PromptInputActionAddAttachments,
  PromptInputActionMenu,
  PromptInputActionMenuContent,
  PromptInputActionMenuTrigger,
  PromptInputAttachment,
  PromptInputAttachments,
  PromptInputBody,
  PromptInputButton,
  PromptInputHeader,
  type PromptInputMessage,
  PromptInputSelect,
  PromptInputSelectContent,
  PromptInputSelectItem,
  PromptInputSelectTrigger,
  PromptInputSelectValue,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputFooter,
  PromptInputTools,
} from '@/components/ai-elements/prompt-input';
import { GlobeIcon } from 'lucide-react';
import type { ChatStatus } from 'ai';

export interface Model {
  name: string;
  value: string;
}

export interface ChatInputBarProps {
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (message: PromptInputMessage) => void;
  models: Model[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  webSearch: boolean;
  onWebSearchToggle: () => void;
  status?: ChatStatus;
  disabled?: boolean;
}

export function ChatInputBar({
  input,
  onInputChange,
  onSubmit,
  models,
  selectedModel,
  onModelChange,
  webSearch,
  onWebSearchToggle,
  status,
  disabled = false,
}: ChatInputBarProps) {
  return (
    <PromptInput onSubmit={onSubmit} className="mt-4" globalDrop multiple>
      <PromptInputHeader>
        <PromptInputAttachments>
          {(attachment) => <PromptInputAttachment data={attachment} />}
        </PromptInputAttachments>
      </PromptInputHeader>
      <PromptInputBody>
        <PromptInputTextarea
          onChange={(e) => onInputChange(e.target.value)}
          value={input}
          disabled={disabled}
        />
      </PromptInputBody>
      <PromptInputFooter>
        <PromptInputTools>
          <PromptInputActionMenu>
            <PromptInputActionMenuTrigger />
            <PromptInputActionMenuContent>
              <PromptInputActionAddAttachments />
            </PromptInputActionMenuContent>
          </PromptInputActionMenu>
          <PromptInputButton variant={webSearch ? 'default' : 'ghost'} onClick={onWebSearchToggle}>
            <GlobeIcon className="size-4" />
            <span>Search</span>
          </PromptInputButton>
          <PromptInputSelect onValueChange={onModelChange} value={selectedModel}>
            <PromptInputSelectTrigger>
              <PromptInputSelectValue />
            </PromptInputSelectTrigger>
            <PromptInputSelectContent>
              {models.map((model) => (
                <PromptInputSelectItem key={model.value} value={model.value}>
                  {model.name}
                </PromptInputSelectItem>
              ))}
            </PromptInputSelectContent>
          </PromptInputSelect>
        </PromptInputTools>
        <PromptInputSubmit disabled={!input && !status} status={status} />
      </PromptInputFooter>
    </PromptInput>
  );
}
