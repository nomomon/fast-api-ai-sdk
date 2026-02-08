'use client';

import { createContext, useCallback, useContext, useRef } from 'react';

type NewChatContextValue = {
  registerHandler: (handler: () => void) => () => void;
  requestNewChat: () => void;
};

const NewChatContext = createContext<NewChatContextValue | null>(null);

export function NewChatProvider({ children }: { children: React.ReactNode }) {
  const handlerRef = useRef<(() => void) | null>(null);

  const registerHandler = useCallback((handler: () => void) => {
    handlerRef.current = handler;
    return () => {
      handlerRef.current = null;
    };
  }, []);

  const requestNewChat = useCallback(() => {
    handlerRef.current?.();
  }, []);

  return (
    <NewChatContext.Provider value={{ registerHandler, requestNewChat }}>
      {children}
    </NewChatContext.Provider>
  );
}

export function useNewChat(): NewChatContextValue {
  const ctx = useContext(NewChatContext);
  if (!ctx) {
    throw new Error('useNewChat must be used within NewChatProvider');
  }
  return ctx;
}
