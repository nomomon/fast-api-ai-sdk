'use client';

import type * as React from 'react';

import { SettingsSidebar } from './settings-sidebar';

type SettingsShellProps = {
  children: React.ReactNode;
};

export function SettingsShell({ children }: SettingsShellProps) {
  return (
    <div className="flex min-h-0 w-full flex-1 flex-row">
      <SettingsSidebar />
      {children}
    </div>
  );
}
