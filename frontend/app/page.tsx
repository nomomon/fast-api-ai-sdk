'use client';

import { useChat } from '@ai-sdk/react';
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
} from '@/components/ai-elements/conversation';
import { Message, MessageContent } from '@/components/ai-elements/message';
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputSubmit,
} from '@/components/ai-elements/prompt-input';
import { Loader } from '@/components/ai-elements/loader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header with shadcn Card */}
      <Card className="rounded-none border-x-0 border-t-0">
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">AI Chat Assistant</CardTitle>
        </CardHeader>
      </Card>

      {/* Main chat area with AI Elements Conversation */}
      <div className="flex-1 overflow-hidden">
        <Conversation className="h-full">
          <ConversationContent className="h-full overflow-y-auto p-4">
            {messages.length === 0 ? (
              <ConversationEmptyState>
                <div className="text-center text-muted-foreground py-8">
                  <p className="text-lg font-medium mb-2">Start a conversation</p>
                  <p className="text-sm">Ask me anything and I'll help you out!</p>
                </div>
              </ConversationEmptyState>
            ) : (
              <>
                {messages.map((message) => (
                  <Message
                    key={message.id}
                    from={message.role === 'user' ? 'user' : 'assistant'}
                    className="mb-4"
                  >
                    <MessageContent className="whitespace-pre-wrap break-words">
                      {message.content}
                    </MessageContent>
                  </Message>
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <Message from="assistant">
                      <MessageContent>
                        <Loader className="inline-block" />
                      </MessageContent>
                    </Message>
                  </div>
                )}
              </>
            )}
          </ConversationContent>
        </Conversation>
      </div>

      {/* Input area with AI Elements PromptInput and shadcn styling */}
      <div className="border-t bg-background">
        <Card className="rounded-none border-x-0 border-b-0 shadow-none">
          <CardContent className="p-4">
            <form onSubmit={handleSubmit} className="w-full">
              <PromptInput className="w-full">
                <PromptInputTextarea
                  value={input}
                  onChange={handleInputChange}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="min-h-[60px] max-h-[200px] resize-none"
                />
                <PromptInputSubmit
                  disabled={isLoading || !input.trim()}
                  className={cn('ml-2', isLoading && 'opacity-50 cursor-not-allowed')}
                />
              </PromptInput>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
