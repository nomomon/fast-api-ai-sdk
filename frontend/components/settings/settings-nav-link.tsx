'use client';

import type { LucideIcon } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type SettingsNavLinkProps = {
  href: string;
  children: React.ReactNode;
  icon?: LucideIcon;
  isActive?: boolean;
  className?: string;
};

export function SettingsNavLink({
  href,
  children,
  icon: Icon,
  isActive,
  className,
}: SettingsNavLinkProps) {
  return (
    <Button
      variant="ghost"
      className={cn(
        'h-9 w-full justify-start gap-2 px-3 font-normal',
        isActive && 'bg-accent text-accent-foreground hover:bg-accent',
        className
      )}
      data-state={isActive ? 'active' : undefined}
      asChild
    >
      <Link href={href}>
        {Icon ? <Icon className="size-4 shrink-0 opacity-70" aria-hidden /> : null}
        {children}
      </Link>
    </Button>
  );
}
