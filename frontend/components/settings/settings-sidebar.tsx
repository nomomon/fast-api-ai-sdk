'use client';

import { BookOpen, SlidersHorizontal, Wrench } from 'lucide-react';
import { usePathname } from 'next/navigation';
import type * as React from 'react';

import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

import { SettingsNavLink } from './settings-nav-link';
import { SettingsSearchField } from './settings-search-field';

type SettingsSidebarProps = {
  className?: string;
  profileSlot?: React.ReactNode;
};

function settingsPathActive(pathname: string, href: string): boolean {
  if (href === '/settings') {
    return pathname === '/settings';
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function SettingsSidebar({ className, profileSlot }: SettingsSidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'flex w-60 shrink-0 flex-col gap-3 border-border border-r bg-muted/20 px-3 py-4',
        className
      )}
    >
      {profileSlot ? (
        <>
          {profileSlot}
          <Separator />
        </>
      ) : null}
      <SettingsSearchField />
      <Separator />
      <nav className="flex flex-col gap-0.5" aria-label="Settings sections">
        <SettingsNavLink
          href="/settings"
          icon={SlidersHorizontal}
          isActive={settingsPathActive(pathname, '/settings')}
        >
          General
        </SettingsNavLink>
        <SettingsNavLink
          href="/settings/skills"
          icon={BookOpen}
          isActive={settingsPathActive(pathname, '/settings/skills')}
        >
          Skills
        </SettingsNavLink>
        <SettingsNavLink
          href="/settings/tools"
          icon={Wrench}
          isActive={settingsPathActive(pathname, '/settings/tools')}
        >
          Tools & MCPs
        </SettingsNavLink>
      </nav>
    </aside>
  );
}
