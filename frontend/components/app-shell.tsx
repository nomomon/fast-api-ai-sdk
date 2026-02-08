'use client';

import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';

const SIDEBAR_TRIGGER_CLASS =
  'h-9 w-9 -ml-1 shadow-border-small hover:shadow-border-medium bg-background/80 backdrop-blur-sm border-0 hover:bg-background hover:scale-[1.02] transition-all duration-150 ease';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider
      style={
        {
          '--sidebar-width': '19rem',
        } as React.CSSProperties
      }
    >
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center px-4">
          <SidebarTrigger className={SIDEBAR_TRIGGER_CLASS} />
        </header>
        <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
