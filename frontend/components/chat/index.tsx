'use client';

import { useChat } from '@ai-sdk/react';
import { AlertCircle, Github, PlusIcon } from 'lucide-react';
import Image from 'next/image';
import { useState } from 'react';
import { ChatInput } from '@/components/chat/chat-input';
import { MessageList } from '@/components/chat/message-list';
import { ModelSelector } from '@/components/chat/model-selector';
import { SuggestionCard } from '@/components/chat/suggestion-card';
import { ThemeToggle } from '@/components/theme-toggle';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useDefaultModel } from '@/lib/hooks/use-default-model';
import { UserDropdownButton } from '../user/user-dropdown';
import { DefaultChatTransport } from 'ai';

export function Chat() {
  const [input, setInput] = useState('');

  const {
    modelId: currentModelId,
    setModelId: setCurrentModelId,
    models,
    isLoading: isModelLoading,
    error: modelError,
  } = useDefaultModel();

  const handleModelChange = (newModelId: string) => {
    setCurrentModelId(newModelId);
  };

  const { messages, error, sendMessage, regenerate, setMessages, stop, status } = useChat({
    transport: new DefaultChatTransport({
    api: `${process.env.BASE_BACKEND_URL}/api/chat`,
  }),
  });

  const hasMessages = messages.length > 0;
  const isLoading = status === 'streaming';

  const handleNewChat = () => {
    stop();
    setMessages([]);
    setInput('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage({ text: input }, { body: { modelId: currentModelId } });
    setInput('');
  };

  const suggestions = [
    {
      id: 'alamty-weather-think',
      summary: 'What should I wear at Almaty today? Think',
      prompt:
        'Be extremely concise. Sacrifice grammar for the sake of concision. But think deeply: plan your steps, and execute them.\n\nWhat should I wear at Almaty today?',
    },
  ];

  const handleSuggestionClick = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <div className="absolute top-3 left-3 md:top-4 md:left-4 z-10 flex gap-2 animate-fade-in">
        <Button
          onClick={handleNewChat}
          variant="outline"
          size="icon"
          className="h-9 w-9 shadow-border-small hover:shadow-border-medium bg-background/80 backdrop-blur-sm border-0 hover:bg-background hover:scale-[1.02] transition-all duration-150 ease"
        >
          <PlusIcon className="h-4 w-4" />
        </Button>
        <ThemeToggle />
        <Button
          asChild
          variant="outline"
          size="icon"
          className="h-9 w-9 shadow-border-small hover:shadow-border-medium bg-background/80 backdrop-blur-sm border-0 hover:bg-background hover:scale-[1.02] transition-all duration-150 ease"
        >
          <a
            href="https://github.com/nomomon/fast-api-ai-sdk"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Github className="h-4 w-4" />
          </a>
        </Button>
        <UserDropdownButton />
      </div>
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
                <h1 className="text-lg md:text-xl font-medium text-muted-foreground">AI Chatbot</h1>
              </div>
              <p className="text-2xl md:text-4xl font-medium tracking-tight text-foreground">
                How can I help you today?
              </p>
            </div>
            <div className="w-full animate-slide-up" style={{ animationDelay: '100ms' }}>
              <ChatInput
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
              >
                <ModelSelector
                  modelId={currentModelId}
                  models={models}
                  onModelChange={handleModelChange}
                  isLoading={isModelLoading}
                  error={modelError}
                />
              </ChatInput>
            </div>
            {suggestions.length > 0 && (
              <div className="w-1/3 space-y-2 animate-slide-up" style={{ animationDelay: '150ms' }}>
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
          <MessageList messages={messages} isLoading={isLoading} />
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
              onClick={() => regenerate()}
            >
              Retry
            </Button>
          </Alert>
        </div>
      )}

      {hasMessages && (
        <div className="w-full max-w-4xl mx-auto px-4 md:px-8 pb-6 md:pb-8">
          <ChatInput
            input={input}
            setInput={setInput}
            onSubmit={handleSubmit}
            isLoading={isLoading}
          >
            <ModelSelector
              modelId={currentModelId}
              models={models}
              onModelChange={handleModelChange}
              isLoading={isModelLoading}
              error={modelError}
            />
          </ChatInput>
        </div>
      )}

      <footer className="pb-8 text-center animate-fade-in" style={{ animationDelay: '200ms' }}>
        <p className="text-xs md:text-sm text-muted-foreground">
          The chatbot supports various AI models for different use cases.
        </p>
      </footer>
    </div>
  );
}
