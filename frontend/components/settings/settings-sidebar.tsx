import { Bot, Cpu, Settings2, SlidersHorizontal } from 'lucide-react';
import type * as React from 'react';

import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

import { SettingsNavItem } from './settings-nav-item';
import { SettingsSearchField } from './settings-search-field';

type SettingsSidebarProps = {
  className?: string;
  profileSlot?: React.ReactNode;
};

export function SettingsSidebar({ className, profileSlot }: SettingsSidebarProps) {
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
        <SettingsNavItem icon={SlidersHorizontal} isActive>
          General
        </SettingsNavItem>
        <SettingsNavItem icon={Bot}>Agents</SettingsNavItem>
        <SettingsNavItem icon={Cpu}>Models</SettingsNavItem>
        <SettingsNavItem icon={Settings2}>Advanced</SettingsNavItem>
      </nav>
    </aside>
  );
}
