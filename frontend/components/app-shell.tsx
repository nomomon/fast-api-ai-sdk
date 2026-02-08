'use client';

import { usePathname } from 'next/navigation';
import { AppSidebar } from '@/components/app-sidebar';
import { ThemeToggle } from '@/components/theme-toggle';
import { UserDropdownButton } from '@/components/user/user-dropdown';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb';
import { Separator } from '@/components/ui/separator';
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar';

const PATH_LABELS: Record<string, string> = {
  '/': 'Chat',
  '/dashboard': 'Dashboard',
};

function AppBreadcrumb() {
  const pathname = usePathname();
  const label = PATH_LABELS[pathname] ?? (pathname.slice(1) || 'Chat');

  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbPage>{label}</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );
}

export function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
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
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator
            orientation="vertical"
            className="mr-2 data-[orientation=vertical]:h-4"
          />
          <AppBreadcrumb />
          <div className="ml-auto flex items-center gap-2">
            <ThemeToggle />
            <UserDropdownButton />
          </div>
        </header>
        <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
