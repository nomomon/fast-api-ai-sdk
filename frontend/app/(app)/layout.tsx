import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/app-shell';
import { NewChatProvider } from '@/lib/contexts/new-chat-context';

const COOKIE_NAME = 'auth_token';

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  if (!cookieStore.get(COOKIE_NAME)?.value) {
    redirect('/login');
  }

  const defaultSidebarOpen = cookieStore.get('sidebar_state')?.value !== 'false';

  return (
    <NewChatProvider>
      <AppShell defaultSidebarOpen={defaultSidebarOpen}>{children}</AppShell>
    </NewChatProvider>
  );
}
