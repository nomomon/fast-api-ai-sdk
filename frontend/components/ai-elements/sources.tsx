'use client';

import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import { ExternalLinkIcon } from 'lucide-react';
import type { ComponentProps, HTMLAttributes } from 'react';

export type SourcesProps = ComponentProps<typeof Collapsible>;

export const Sources = ({ className, ...props }: SourcesProps) => (
  <Collapsible className={cn('w-full', className)} {...props} />
);

export type SourcesTriggerProps = ComponentProps<typeof CollapsibleTrigger> & {
  count?: number;
};

export const SourcesTrigger = ({ className, count, children, ...props }: SourcesTriggerProps) => (
  <CollapsibleTrigger asChild>
    <Button
      className={cn('h-auto p-1.5 text-muted-foreground text-xs', className)}
      size="sm"
      type="button"
      variant="ghost"
      {...props}
    >
      {children ?? (
        <>
          <ExternalLinkIcon className="mr-1.5 size-3" />
          {count !== undefined && count > 0 ? `${count} source${count > 1 ? 's' : ''}` : 'Sources'}
        </>
      )}
    </Button>
  </CollapsibleTrigger>
);

export type SourcesContentProps = ComponentProps<typeof CollapsibleContent>;

export const SourcesContent = ({ className, ...props }: SourcesContentProps) => (
  <CollapsibleContent className={cn('mt-2', className)} {...props} />
);

export type SourceProps = HTMLAttributes<HTMLAnchorElement> & {
  href: string;
  title?: string;
};

export const Source = ({ className, href, title, children, ...props }: SourceProps) => (
  <a
    className={cn(
      'flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-muted-foreground text-sm transition-colors hover:bg-accent hover:text-accent-foreground',
      className
    )}
    href={href}
    rel="noopener noreferrer"
    target="_blank"
    {...props}
  >
    <ExternalLinkIcon className="size-3 shrink-0" />
    <span className="truncate">{children ?? title ?? href}</span>
  </a>
);
