'use client';

import { Copy, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AgentMessageActionsProps {
  onRegenerate: () => void;
  onCopy: () => void;
  isStreaming: boolean;
}

export function AgentMessageActions({
  onRegenerate,
  onCopy,
  isStreaming,
}: AgentMessageActionsProps) {
  const handleCopy = () => {
    try {
      onCopy();
      toast.success('Copied to clipboard');
    } catch {
      toast.error('Failed to copy');
    }
  };

  return (
    <div
      className={cn('flex gap-2 mt-2 transition-opacity', {
        'opacity-0 hidden': isStreaming,
      })}
    >
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onRegenerate}
        disabled={isStreaming}
        aria-label="Regenerate response"
        className="text-muted-foreground hover:text-foreground"
      >
        <RefreshCw className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={handleCopy}
        aria-label="Copy message"
        className="text-muted-foreground hover:text-foreground"
      >
        <Copy className="h-4 w-4" />
      </Button>
    </div>
  );
}
