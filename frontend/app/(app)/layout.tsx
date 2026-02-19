import { cookies } from 'next/headers';
import { AppShell } from '@/components/app-shell';
import { NewChatProvider } from '@/lib/contexts/new-chat-context';

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const defaultSidebarOpen = cookieStore.get('sidebar_state')?.value !== 'false';

  return (
    <NewChatProvider>
      <AppShell defaultSidebarOpen={defaultSidebarOpen}>{children}</AppShell>
    </NewChatProvider>
  );
}
