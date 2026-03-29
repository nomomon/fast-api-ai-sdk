import type * as React from 'react';

import { cn } from '@/lib/utils';

export function SettingsSectionLabel({ className, ...props }: React.ComponentProps<'p'>) {
  return (
    <p
      className={cn('text-muted-foreground text-xs font-medium tracking-wide uppercase', className)}
      {...props}
    />
  );
}
