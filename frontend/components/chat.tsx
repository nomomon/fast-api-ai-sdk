'use client';

import { useChat } from '@ai-sdk/react';
import { AlertCircle, Github, PlusIcon } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Streamdown } from 'streamdown';
import { Reasoning, ReasoningContent, ReasoningTrigger } from '@/components/ai-elements/reasoning';
import { ChatInput } from '@/components/chat-input';
import { ThemeToggle } from '@/components/theme-toggle';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useDefaultModel } from '@/lib/hooks/use-default-model';
import { cn } from '@/lib/utils';

export function Chat() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  const { messages, error, sendMessage, regenerate, setMessages, stop, status } = useChat();

  const hasMessages = messages.length > 0;

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom]);

  const handleNewChat = () => {
    stop();
    setMessages([]);
    setInput('');
  };

  const isLoading = status === 'streaming';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage({ text: input }, { body: { modelId: currentModelId } });
    setInput('');
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
      </div>
      {!hasMessages && (
        <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-8 animate-fade-in">
          <div className="w-full max-w-2xl text-center space-y-8 md:space-y-12">
            <h1 className="text-3xl md:text-6xl font-light tracking-tight text-foreground animate-slide-up">
              <span className="font-mono font-semibold tracking-tight bg-foreground text-background px-4 py-3 rounded-2xl shadow-border-medium">
                AI CHATBOT
              </span>
            </h1>
            <div className="w-full animate-slide-up" style={{ animationDelay: '100ms' }}>
              <ChatInput
                input={input}
                setInput={setInput}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                modelId={currentModelId}
                onModelChange={handleModelChange}
                models={models}
                isModelLoading={isModelLoading}
                modelError={modelError}
              />
            </div>
          </div>
        </div>
      )}

      {hasMessages && (
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full animate-fade-in overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 md:px-8 py-4 hide-scrollbar">
            <div className="flex flex-col gap-4 md:gap-6 pb-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    m.role === 'user' &&
                      'bg-foreground text-background rounded-2xl p-3 md:p-4 ml-auto max-w-[90%] md:max-w-[75%] shadow-border-small font-medium text-sm md:text-base',
                    m.role === 'assistant' &&
                      'max-w-[95%] md:max-w-[85%] text-foreground/90 leading-relaxed text-sm md:text-base'
                  )}
                >
                  {/* Handle reasoning parts separately if they exist */}
                  {m.role === 'assistant' && m.parts.some((part) => part.type === 'reasoning') && (
                    <Reasoning
                      isStreaming={
                        status === 'streaming' && m.id === messages[messages.length - 1]?.id
                      }
                    >
                      <ReasoningTrigger />
                      <ReasoningContent>
                        {m.parts
                          .filter((part) => part.type === 'reasoning')
                          .map((part) => part.text || '')
                          .join('')}
                      </ReasoningContent>
                    </Reasoning>
                  )}

                  {/* Handle text and other parts */}
                  {m.parts.map((part, i) => {
                    switch (part.type) {
                      case 'text':
                        return m.role === 'assistant' ? (
                          <Streamdown
                            key={`${m.id}-${i}`}
                            isAnimating={
                              status === 'streaming' && m.id === messages[messages.length - 1]?.id
                            }
                          >
                            {part.text}
                          </Streamdown>
                        ) : (
                          <div key={`${m.id}-${i}`}>{part.text}</div>
                        );
                      case 'reasoning':
                        // Reasoning parts are handled above
                        return null;
                      default:
                        return null;
                    }
                  })}
                </div>
              ))}

              <div ref={messagesEndRef} />
            </div>
          </div>
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
            modelId={currentModelId}
            onModelChange={handleModelChange}
            models={models}
            isModelLoading={isModelLoading}
            modelError={modelError}
          />
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
