import type * as React from 'react';

import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

type SettingsSearchFieldProps = {
  /** Omit shortcut: pass `null` or `""`. Default when unset: `⌘F`. */
  shortcutHint?: string | null;
} & React.ComponentProps<typeof Input>;

export function SettingsSearchField({
  className,
  placeholder = 'Search settings',
  shortcutHint,
  ...props
}: SettingsSearchFieldProps) {
  const hint = shortcutHint === undefined ? '⌘F' : shortcutHint;

  return (
    <div className="relative">
      <Input
        className={cn('h-9 bg-muted/40 shadow-none', hint ? 'pr-14' : 'pr-3', className)}
        placeholder={placeholder}
        {...props}
      />
      {hint ? (
        <kbd className="pointer-events-none absolute top-1/2 right-2 -translate-y-1/2 rounded border border-border bg-background/80 px-1.5 py-0.5 font-sans text-[10px] text-muted-foreground">
          {hint}
        </kbd>
      ) : null}
    </div>
  );
}
