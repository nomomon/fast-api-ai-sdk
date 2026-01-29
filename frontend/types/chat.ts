import type { UseChatHelpers } from '@ai-sdk/react';
import type { UIMessage } from 'ai';

type ChatMetadata = Record<string, never>;

/**
 * Research workflow: search X websites → search more → status "generating" → LLM streams text.
 * Each data part maps to a stream event type: data-search, data-status.
 */
export type WorkflowSearchData = {
  /** URLs of websites found in this search round */
  websites: string[];
  /** 1-based round number (first search = 1, second = 2, etc.) */
  round: number;
  /** Optional query that was searched */
  query?: string;
  /** Step status for UI */
  status?: 'active' | 'complete';
};

export type WorkflowStatusData = {
  /** Human-readable status message, e.g. "Generating concise response..." */
  message: string;
  /** Phase identifier for icon/UX mapping */
  phase: 'generating' | 'synthesizing' | 'analyzing' | 'complete' | (string & {});
};

export type ChatDataParts = {
  search: WorkflowSearchData;
  status: WorkflowStatusData;
};

export type ChatMessage = UIMessage<ChatMetadata, ChatDataParts>;
export type UseChat = UseChatHelpers<ChatMessage>;
