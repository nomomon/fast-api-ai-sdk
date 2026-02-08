'use client';

import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider, SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';

function FloatingSidebarTrigger() {
  const { open, isMobile } = useSidebar();
  return (
    <SidebarTrigger
      className={cn(
        'fixed top-4 z-50 h-9 w-9 -ml-1 border-0 bg-background/40 shadow-border-small backdrop-blur-sm transition-[left,transform] duration-200 ease-linear hover:bg-background hover:shadow-border-medium hover:scale-[1.02]',
        isMobile || !open ? 'left-4' : 'left-[calc(var(--sidebar-width)+0.5rem)]'
      )}
    />
  );
}

export function AppShell({
  children,
  defaultSidebarOpen,
}: {
  children: React.ReactNode;
  defaultSidebarOpen?: boolean;
}) {
  return (
    <SidebarProvider
      defaultOpen={defaultSidebarOpen}
      style={
        {
          '--sidebar-width': '19rem',
        } as React.CSSProperties
      }
    >
      <AppSidebar />
      <FloatingSidebarTrigger />
      <SidebarInset>
        <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
