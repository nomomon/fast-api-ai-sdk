'use client';

import { Loader2 } from 'lucide-react';
import { memo } from 'react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { DisplayAgent } from '@/lib/interfaces/display-agent';

type AgentSelectorProps = {
  agentId: string;
  agents: DisplayAgent[];
  onAgentChange: (agentId: string) => void;
  isLoading: boolean;
  error: Error | null;
};

export const AgentSelector = memo(function AgentSelector({
  agentId,
  agents,
  onAgentChange,
  isLoading,
  error,
}: AgentSelectorProps) {
  return (
    <Select
      value={agentId}
      onValueChange={onAgentChange}
      disabled={isLoading || !!error || !agents.length}
    >
      <SelectTrigger
        aria-label="Choose agent"
        className="w-fit border-0 bg-transparent focus:ring-0 focus:ring-offset-0 focus:outline-none focus-visible:outline-none focus:border-0 focus-visible:border-0 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl font-medium text-xs p-1 pl-2 shadow-none gap-1! h-8!"
      >
        <div className="flex items-center gap-2 w-full">
          {isLoading ? (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              <span className="text-xs">Loading</span>
            </>
          ) : error ? (
            <span className="text-red-500 text-xs">Error</span>
          ) : !agents.length ? (
            <span className="text-xs">No agents</span>
          ) : (
            <SelectValue placeholder="Select agent" />
          )}
        </div>
      </SelectTrigger>

      <SelectContent
        className="rounded-2xl border-0 shadow-border-medium bg-popover/95 backdrop-blur-sm animate-scale-in"
        align="start"
        sideOffset={4}
      >
        <SelectGroup>
          <SelectLabel className="text-xs text-muted-foreground px-2 py-1">Agents</SelectLabel>
          {agents.map((agent) => (
            <SelectItem
              key={agent.id}
              value={agent.id}
              textValue={agent.label}
              className="rounded-lg transition-colors duration-150 ease-out data-[state=checked]:font-medium text-xs"
            >
              <span>{agent.label}</span>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
});
