'use client';

import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import type { PromptInputMessage } from '@/components/ai-elements/prompt-input';
import { useState } from 'react';
import { useChat } from '@ai-sdk/react';
import { ChatInputBar } from '@/components/chat/ChatInputBar';
import { MessagesList } from '@/components/chat/MessagesList';
import { MODELS } from '@/lib/constants';

const ChatBotDemo = () => {
  const [input, setInput] = useState('');
  const [model, setModel] = useState<string>(MODELS[0].value);
  const [webSearch, setWebSearch] = useState(false);
  const { messages, sendMessage, status, regenerate } = useChat();

  const handleSubmit = (message: PromptInputMessage) => {
    const hasText = Boolean(message.text);
    const hasAttachments = Boolean(message.files?.length);

    if (!(hasText || hasAttachments)) {
      return;
    }

    sendMessage(
      {
        text: message.text || 'Sent with attachments',
        files: message.files,
      },
      {
        body: {
          model: model,
          webSearch: webSearch,
        },
      }
    );
    setInput('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 relative size-full h-screen">
      <div className="flex flex-col h-full">
        <Conversation className="h-full">
          <ConversationContent>
            <MessagesList messages={messages} status={status} onRegenerate={regenerate} />
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>

        <ChatInputBar
          input={input}
          onInputChange={setInput}
          onSubmit={handleSubmit}
          models={MODELS}
          selectedModel={model}
          onModelChange={setModel}
          webSearch={webSearch}
          onWebSearchToggle={() => setWebSearch(!webSearch)}
          status={status}
          disabled={status === 'submitted' || status === 'streaming'}
        />
      </div>
    </div>
  );
};

export default ChatBotDemo;
