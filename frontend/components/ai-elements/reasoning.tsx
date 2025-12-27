'use client';

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import { BrainIcon } from 'lucide-react';
import type { ComponentProps, HTMLAttributes } from 'react';

export type ReasoningProps = ComponentProps<typeof Collapsible> & {
  isStreaming?: boolean;
};

export const Reasoning = ({ className, isStreaming, ...props }: ReasoningProps) => (
  <Collapsible className={cn('w-full', className)} defaultOpen={isStreaming} {...props} />
);

export type ReasoningTriggerProps = ComponentProps<typeof CollapsibleTrigger>;

export const ReasoningTrigger = ({ className, children, ...props }: ReasoningTriggerProps) => (
  <CollapsibleTrigger
    className={cn(
      'flex w-full items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-left text-muted-foreground text-sm transition-colors hover:bg-muted',
      className
    )}
    {...props}
  >
    <BrainIcon className="size-4 shrink-0" />
    <span className="font-medium">Reasoning</span>
    {children}
  </CollapsibleTrigger>
);

export type ReasoningContentProps = ComponentProps<typeof CollapsibleContent>;

export const ReasoningContent = ({ className, children, ...props }: ReasoningContentProps) => (
  <CollapsibleContent className={cn('mt-2', className)} {...props}>
    <div className="rounded-md border border-border bg-muted/30 p-3 text-muted-foreground text-sm whitespace-pre-wrap">
      {children}
    </div>
  </CollapsibleContent>
);
