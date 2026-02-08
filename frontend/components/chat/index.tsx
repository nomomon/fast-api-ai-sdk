'use client';

import { useChat } from '@ai-sdk/react';
import { AlertCircle } from 'lucide-react';
import Image from 'next/image';
import { signOut } from 'next-auth/react';
import { useCallback, useEffect, useState } from 'react';
import { AgentSelector } from '@/components/chat/agent-selector';
import { ChatInput } from '@/components/chat/chat-input';
import { MessageList } from '@/components/chat/message-list';
import { ModelSelector } from '@/components/chat/model-selector';
import { PromptSelector } from '@/components/chat/prompt-selector';
import { SuggestionCard } from '@/components/chat/suggestion-card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useNewChat } from '@/lib/contexts/new-chat-context';
import { useDefaultAgent } from '@/lib/hooks/use-default-agent';
import { useDefaultModel } from '@/lib/hooks/use-default-model';
import { useDefaultPrompt } from '@/lib/hooks/use-default-prompt';
import type { ChatMessage } from '@/types/chat';

export function Chat() {
  const [input, setInput] = useState('');

  const {
    modelId: currentModelId,
    setModelId: setCurrentModelId,
    models,
    isLoading: isModelLoading,
    error: modelError,
  } = useDefaultModel();

  const {
    promptId: currentPromptId,
    setPromptId: setCurrentPromptId,
    prompts,
    isLoading: isPromptLoading,
    error: promptError,
  } = useDefaultPrompt();

  const {
    agentId: currentAgentId,
    setAgentId: setCurrentAgentId,
    agents,
    isLoading: isAgentLoading,
    error: agentError,
  } = useDefaultAgent();

  const handleModelChange = (newModelId: string) => {
    setCurrentModelId(newModelId);
  };

  const handlePromptChange = (newPromptId: string) => {
    setCurrentPromptId(newPromptId);
  };

  const handleAgentChange = (newAgentId: string) => {
    setCurrentAgentId(newAgentId);
  };

  const { messages, error, sendMessage, regenerate, setMessages, stop, status } =
    useChat<ChatMessage>({
      onError: (err) => {
        // TODO: this looks quite hacky
        if (JSON.parse(err.message).error === 'Unauthorized') {
          signOut({ callbackUrl: '/login' });
        }
      },
    });

  const hasMessages = messages.length > 0;
  const isLoading = status === 'streaming';

  const { registerHandler } = useNewChat();

  const handleNewChat = useCallback(() => {
    stop();
    setMessages([]);
    setInput('');
  }, [stop, setMessages]);

  useEffect(() => {
    return registerHandler(handleNewChat);
  }, [registerHandler, handleNewChat]);

  const chatBody = {
    modelId: currentModelId,
    promptId: currentPromptId,
    agentId: currentAgentId || 'chat',
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage({ text: input }, { body: chatBody });
    setInput('');
  };

  const suggestions = [
    {
      id: 'almaty-weather-think',
      summary: 'What should I wear at Almaty today?',
      prompt: 'What should I wear at Almaty today?',
    },
  ];

  const handleSuggestionClick = (prompt: string) => {
    sendMessage({ text: prompt }, { body: chatBody });
  };

  const handleRegenerate = (messageId: string) => {
    regenerate({ messageId, body: chatBody });
  };

  const handleEdit = (messageId: string, newText: string) => {
    sendMessage({ text: newText, messageId }, { body: chatBody });
  };

  const EnhancedChatInput = (
    <ChatInput input={input} setInput={setInput} onSubmit={handleSubmit} isLoading={isLoading}>
      <ModelSelector
        modelId={currentModelId}
        models={models}
        onModelChange={handleModelChange}
        isLoading={isModelLoading}
        error={modelError}
      />
      <AgentSelector
        agentId={currentAgentId}
        agents={agents}
        onAgentChange={handleAgentChange}
        isLoading={isAgentLoading}
        error={agentError}
      />
      <PromptSelector
        promptId={currentPromptId}
        prompts={prompts}
        onPromptChange={handlePromptChange}
        isLoading={isPromptLoading}
        error={promptError}
      />
    </ChatInput>
  );

  return (
    <div className="flex flex-1 flex-col min-h-0 overflow-hidden">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-background focus:rounded-md focus:ring-2 focus:ring-ring focus:outline-none"
      >
        Skip to main content
      </a>
      <main id="main-content" className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {!hasMessages && (
          <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-8 animate-fade-in">
            <div className="w-full max-w-2xl space-y-8 md:space-y-12">
              <div className="flex flex-col gap-6 animate-slide-up">
                <div className="flex flex-row items-center gap-3">
                  <Image
                    src="/icons/app-icon.svg"
                    alt="AI Chatbot"
                    className="h-8 w-8 md:h-10 md:w-10 border-2 border-gray-200 rounded-md"
                    width={40}
                    height={40}
                  />
                  <h1 className="text-lg md:text-xl font-medium text-muted-foreground">
                    AI Chatbot
                  </h1>
                </div>
                <p className="text-2xl md:text-4xl font-medium tracking-tight text-foreground">
                  How can I help you today?
                </p>
              </div>
              <div className="w-full animate-slide-up" style={{ animationDelay: '100ms' }}>
                {EnhancedChatInput}
              </div>
              {suggestions.length > 0 && (
                <div
                  className="w-1/3 space-y-2 animate-slide-up"
                  style={{ animationDelay: '150ms' }}
                >
                  {suggestions.map((suggestion) => (
                    <SuggestionCard
                      key={suggestion.id}
                      summary={suggestion.summary}
                      prompt={suggestion.prompt}
                      onClick={handleSuggestionClick}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {hasMessages && (
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full animate-fade-in overflow-hidden">
            <MessageList
              messages={messages}
              isLoading={isLoading}
              onRegenerate={handleRegenerate}
              onEdit={handleEdit}
            />
          </div>
        )}

        {error && (
          <div className="max-w-4xl mx-auto w-full px-4 md:px-8 pb-4 animate-slide-down">
            <Alert variant="destructive" className="flex flex-col items-end">
              <div className="flex flex-row gap-2">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <AlertDescription className="dark:text-red-400 text-red-600">
                  'An error occurred while generating the response.'
                </AlertDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="ml-auto transition-all duration-150 ease-out hover:scale-105"
                onClick={() => regenerate({ body: chatBody })}
              >
                Retry
              </Button>
            </Alert>
          </div>
        )}

        {hasMessages && (
          <div className="w-full max-w-4xl mx-auto px-4 md:px-8 pb-6 md:pb-8">
            {EnhancedChatInput}
          </div>
        )}
      </main>

      <footer className="pb-8 text-center animate-fade-in" style={{ animationDelay: '200ms' }}>
        <p className="text-xs md:text-sm text-muted-foreground">
          The chatbot supports various AI models for different use cases.
        </p>
      </footer>
    </div>
  );
}
