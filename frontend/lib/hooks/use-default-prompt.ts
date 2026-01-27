import { useEffect, useState } from 'react';
import { useAvailablePrompts } from '@/lib/hooks/use-available-prompts';

export function useDefaultPrompt() {
  const { prompts, isLoading, error } = useAvailablePrompts();
  const [promptId, setPromptId] = useState<string>('');

  useEffect(() => {
    // if the request is still loading, do nothing
    if (isLoading || !prompts || prompts.length === 0) return;

    // if promptId is already set, do nothing (preserve user selection)
    if (promptId) return;

    const savedPromptId = localStorage.getItem('default-prompt');

    if (savedPromptId && prompts.some((p) => p.id === savedPromptId)) {
      setPromptId(savedPromptId);
    } else {
      setPromptId(prompts[0].id);
    }
  }, [prompts, isLoading, promptId]);

  const handlePromptChange = (id: string) => {
    setPromptId(id);
    localStorage.setItem('default-prompt', id);
  };

  return { promptId, setPromptId: handlePromptChange, prompts, isLoading, error };
}
