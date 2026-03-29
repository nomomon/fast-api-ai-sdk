import type { LucideIcon } from 'lucide-react';
import type * as React from 'react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type SettingsNavItemProps = {
  children: React.ReactNode;
  icon?: LucideIcon;
  isActive?: boolean;
  className?: string;
} & React.ComponentProps<'button'>;

export function SettingsNavItem({
  children,
  icon: Icon,
  isActive,
  className,
  type = 'button',
  ...props
}: SettingsNavItemProps) {
  return (
    <Button
      type={type}
      variant="ghost"
      className={cn(
        'h-9 w-full justify-start gap-2 px-3 font-normal',
        isActive && 'bg-accent text-accent-foreground hover:bg-accent',
        className
      )}
      data-state={isActive ? 'active' : undefined}
      {...props}
    >
      {Icon ? <Icon className="size-4 shrink-0 opacity-70" aria-hidden /> : null}
      {children}
    </Button>
  );
}
