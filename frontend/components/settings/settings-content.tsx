import type * as React from 'react';

import { cn } from '@/lib/utils';

import { SettingsSectionLabel } from './settings-section-label';

type SettingsContentProps = {
  title: string;
  children?: React.ReactNode;
  className?: string;
};

export function SettingsContent({ title, children, className }: SettingsContentProps) {
  return (
    <div
      className={cn(
        'flex min-h-0 min-w-0 flex-1 flex-col gap-6 overflow-auto px-6 py-6',
        className
      )}
    >
      <h1 className="font-semibold text-2xl tracking-tight">{title}</h1>
      <div className="flex flex-col gap-6">
        <section className="flex flex-col gap-3">
          <SettingsSectionLabel>Preferences</SettingsSectionLabel>
          <p className="text-muted-foreground text-sm">
            Placeholder for preferences. Replace with real settings when ready.
          </p>
        </section>
        {children}
      </div>
    </div>
  );
}
