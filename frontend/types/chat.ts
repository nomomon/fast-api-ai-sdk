import type { UseChatHelpers } from '@ai-sdk/react';
import type { UIMessage } from 'ai';

type ChatMetadata = Record<string, never>;

/**
 * Start status: shown in header when workflow begins. Not rendered in chain of thought.
 */
export type WorkflowStartLabelData = {
  label: string;
};

/**
 * End status: shown in header when workflow completes. Not rendered in chain of thought.
 */
export type WorkflowEndLabelData = {
  label: string;
};

/**
 * Workflow step: rendered in the chain of thought.
 */
export type WorkflowStepData = {
  label: string;
  details?: string[];
  type?: 'search' | 'status';
};

export type ChatDataParts = {
  'start-label': WorkflowStartLabelData;
  step: WorkflowStepData;
  'end-label': WorkflowEndLabelData;
};

export type ChatMessage = UIMessage<ChatMetadata, ChatDataParts>;
export type UseChat = UseChatHelpers<ChatMessage>;
