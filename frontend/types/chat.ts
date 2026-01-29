import type { UseChatHelpers } from '@ai-sdk/react';
import type { UIMessage } from 'ai';

type ChatMetadata = Record<string, never>;

type ChatDataParts = {
  search: { files: string[] };
};

export type ChatMessage = UIMessage<ChatMetadata, ChatDataParts>;
export type UseChat = UseChatHelpers<ChatMessage>;
export type { ChatDataParts };
