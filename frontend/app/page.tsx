'use client';

import { useState } from 'react';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { Card } from '@/components/ui/card';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Message = { role: 'user' | 'assistant'; content: string };

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // TODO: Integrate ai/sdk for streaming when backend streaming route is implemented

  const handleSendMessage = async (message: string) => {
    setIsLoading(true);

    // Add user message to local state
    const userMessage: Message = { role: 'user', content: message };
    setMessages((prev: Message[]) => [...prev, userMessage]);

    try {
      // For now, we'll use a simple fetch approach
      // The ai/sdk integration will be fully implemented when backend streaming is ready
      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Add assistant response
      setMessages((prev: Message[]) => [
        ...prev,
        { role: 'assistant', content: data.message || 'No response' },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev: Message[]) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-background">
      <Card className="w-full max-w-4xl h-[600px] flex flex-col">
        <div className="border-b p-4">
          <h1 className="text-2xl font-bold">AI Chatbot</h1>
          <p className="text-sm text-muted-foreground">Powered by FastAPI and Next.js</p>
        </div>
        <ChatContainer
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </Card>
    </main>
  );
}
