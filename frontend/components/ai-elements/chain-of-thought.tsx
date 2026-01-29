'use client';

import { useControllableState } from '@radix-ui/react-use-controllable-state';
import { BrainIcon, ChevronDownIcon, DotIcon, type LucideIcon } from 'lucide-react';
import type { ComponentProps, ReactNode } from 'react';
import { createContext, memo, useContext, useEffect, useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';

type ChainOfThoughtContextValue = {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  isStreaming: boolean;
};

const ChainOfThoughtContext = createContext<ChainOfThoughtContextValue | null>(null);

const useChainOfThought = () => {
  const context = useContext(ChainOfThoughtContext);
  if (!context) {
    throw new Error('ChainOfThought components must be used within ChainOfThought');
  }
  return context;
};

const AUTO_CLOSE_DELAY = 1000;

export type ChainOfThoughtProps = ComponentProps<'div'> & {
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  isStreaming?: boolean;
};

export const ChainOfThought = memo(
  ({
    className,
    open,
    defaultOpen = false,
    onOpenChange,
    isStreaming = false,
    children,
    ...props
  }: ChainOfThoughtProps) => {
    const [isOpen, setIsOpen] = useControllableState({
      prop: open,
      defaultProp: defaultOpen,
      onChange: onOpenChange,
    });
    const [hasAutoClosed, setHasAutoClosed] = useState(false);

    // Auto-close when streaming ends (once only)
    useEffect(() => {
      if (defaultOpen && !isStreaming && isOpen && !hasAutoClosed) {
        const timer = setTimeout(() => {
          setIsOpen(false);
          setHasAutoClosed(true);
        }, AUTO_CLOSE_DELAY);
        return () => clearTimeout(timer);
      }
    }, [isStreaming, isOpen, defaultOpen, setIsOpen, hasAutoClosed]);

    const chainOfThoughtContext = useMemo(
      () => ({ isOpen, setIsOpen, isStreaming }),
      [isOpen, setIsOpen, isStreaming]
    );

    return (
      <ChainOfThoughtContext.Provider value={chainOfThoughtContext}>
        <div className={cn('not-prose mb-4 max-w-prose space-y-4', className)} {...props}>
          {children}
        </div>
      </ChainOfThoughtContext.Provider>
    );
  }
);

export type ChainOfThoughtHeaderProps = ComponentProps<typeof CollapsibleTrigger> & {
  getHeaderMessage?: (isStreaming: boolean) => ReactNode;
};

export const ChainOfThoughtHeader = memo(
  ({ className, children, getHeaderMessage, ...props }: ChainOfThoughtHeaderProps) => {
    const { isOpen, setIsOpen, isStreaming } = useChainOfThought();

    const headerContent =
      children ?? (getHeaderMessage ? getHeaderMessage(isStreaming) : 'Chain of Thought');

    return (
      <Collapsible onOpenChange={setIsOpen} open={isOpen}>
        <CollapsibleTrigger
          className={cn(
            'flex w-full items-center gap-2 text-muted-foreground text-sm transition-colors hover:text-foreground',
            className
          )}
          {...props}
        >
          <BrainIcon className="size-4" />
          <span className="flex-1 text-left">{headerContent}</span>
          <ChevronDownIcon
            className={cn('size-4 transition-transform', isOpen ? 'rotate-180' : 'rotate-0')}
          />
        </CollapsibleTrigger>
      </Collapsible>
    );
  }
);

export type ChainOfThoughtStepProps = ComponentProps<'div'> & {
  icon?: LucideIcon;
  iconClassName?: string;
  label: ReactNode;
  description?: ReactNode;
  status?: 'complete' | 'active' | 'pending';
};

export const ChainOfThoughtStep = memo(
  ({
    className,
    icon: Icon = DotIcon,
    iconClassName,
    label,
    description,
    status = 'complete',
    children,
    ...props
  }: ChainOfThoughtStepProps) => {
    const statusStyles = {
      complete: 'text-muted-foreground',
      active: 'text-foreground',
      pending: 'text-muted-foreground/50',
    };

    return (
      <div
        className={cn(
          'flex gap-2 text-sm',
          statusStyles[status],
          'fade-in-0 slide-in-from-top-2 animate-in',
          className
        )}
        {...props}
      >
        <div className="relative mt-0.5">
          <Icon className={cn('size-4', iconClassName)} />
          <div className="-mx-px absolute top-7 bottom-0 left-1/2 w-px bg-border" />
        </div>
        <div className="flex-1 space-y-2 overflow-hidden">
          <div>{label}</div>
          {description && <div className="text-muted-foreground text-xs">{description}</div>}
          {children}
        </div>
      </div>
    );
  }
);

export type ChainOfThoughtSearchResultsProps = ComponentProps<'div'>;

export const ChainOfThoughtSearchResults = memo(
  ({ className, ...props }: ChainOfThoughtSearchResultsProps) => (
    <div className={cn('flex flex-wrap items-center gap-2', className)} {...props} />
  )
);

export type ChainOfThoughtSearchResultProps = ComponentProps<typeof Badge>;

export const ChainOfThoughtSearchResult = memo(
  ({ className, children, ...props }: ChainOfThoughtSearchResultProps) => (
    <Badge
      className={cn('gap-1 px-2 py-0.5 font-normal text-xs', className)}
      variant="secondary"
      {...props}
    >
      {children}
    </Badge>
  )
);

export type ChainOfThoughtContentProps = ComponentProps<typeof CollapsibleContent>;

export const ChainOfThoughtContent = memo(
  ({ className, children, ...props }: ChainOfThoughtContentProps) => {
    const { isOpen } = useChainOfThought();

    return (
      <Collapsible open={isOpen}>
        <CollapsibleContent
          className={cn(
            'mt-2 space-y-3',
            'data-[state=closed]:fade-out-0 data-[state=closed]:slide-out-to-top-2 data-[state=open]:slide-in-from-top-2 text-popover-foreground outline-none data-[state=closed]:animate-out data-[state=open]:animate-in',
            className
          )}
          {...props}
        >
          {children}
        </CollapsibleContent>
      </Collapsible>
    );
  }
);

export type ChainOfThoughtImageProps = ComponentProps<'div'> & {
  caption?: string;
};

export const ChainOfThoughtImage = memo(
  ({ className, children, caption, ...props }: ChainOfThoughtImageProps) => (
    <div className={cn('mt-2 space-y-2', className)} {...props}>
      <div className="relative flex max-h-[22rem] items-center justify-center overflow-hidden rounded-lg bg-muted p-3">
        {children}
      </div>
      {caption && <p className="text-muted-foreground text-xs">{caption}</p>}
    </div>
  )
);

ChainOfThought.displayName = 'ChainOfThought';
ChainOfThoughtHeader.displayName = 'ChainOfThoughtHeader';
ChainOfThoughtStep.displayName = 'ChainOfThoughtStep';
ChainOfThoughtSearchResults.displayName = 'ChainOfThoughtSearchResults';
ChainOfThoughtSearchResult.displayName = 'ChainOfThoughtSearchResult';
ChainOfThoughtContent.displayName = 'ChainOfThoughtContent';
ChainOfThoughtImage.displayName = 'ChainOfThoughtImage';
