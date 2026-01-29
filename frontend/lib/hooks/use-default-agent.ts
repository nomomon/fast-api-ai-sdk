import { useEffect, useState } from 'react';
import type { DisplayAgent } from '@/lib/interfaces/display-agent';

const AGENTS: DisplayAgent[] = [
  { id: 'chat', label: 'Chat' },
  { id: 'research', label: 'Research' },
];

export function useDefaultAgent() {
  const [agentId, setAgentId] = useState<string>('');

  useEffect(() => {
    if (agentId) return;

    const savedAgentId = localStorage.getItem('default-agent');

    if (savedAgentId && AGENTS.some((a) => a.id === savedAgentId)) {
      setAgentId(savedAgentId);
    } else {
      setAgentId('chat');
    }
  }, [agentId]);

  const handleAgentChange = (id: string) => {
    setAgentId(id);
    localStorage.setItem('default-agent', id);
  };

  return {
    agentId,
    setAgentId: handleAgentChange,
    agents: AGENTS,
    isLoading: false,
    error: null,
  };
}
