import type * as React from 'react';

import { cn } from '@/lib/utils';

import { SettingsSectionLabel } from './settings-section-label';

type SettingsContentProps = {
  title: string;
  children?: React.ReactNode;
  className?: string;
  /** Shown below the page title when set. */
  description?: string;
  /** When false, hides the General “Preferences” placeholder block. */
  showPreferencesPlaceholder?: boolean;
};

export function SettingsContent({
  title,
  children,
  className,
  description,
  showPreferencesPlaceholder = true,
}: SettingsContentProps) {
  return (
    <div
      className={cn(
        'flex min-h-0 min-w-0 flex-1 flex-col gap-6 overflow-auto px-6 py-6',
        className
      )}
    >
      <div className="flex flex-col gap-1">
        <h1 className="font-semibold text-2xl tracking-tight">{title}</h1>
        {description ? <p className="text-muted-foreground text-sm">{description}</p> : null}
      </div>
      <div className="flex flex-col gap-6">
        {showPreferencesPlaceholder ? (
          <section className="flex flex-col gap-3">
            <SettingsSectionLabel>Preferences</SettingsSectionLabel>
            <p className="text-muted-foreground text-sm">
              Placeholder for preferences. Replace with real settings when ready.
            </p>
          </section>
        ) : null}
        {children}
      </div>
    </div>
  );
}
