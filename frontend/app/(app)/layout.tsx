import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/app-shell';
import { AUTH_COOKIE_NAME } from '@/lib/auth/constants';
import { NewChatProvider } from '@/lib/contexts/new-chat-context';

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  if (!cookieStore.get(AUTH_COOKIE_NAME)?.value) {
    redirect('/login');
  }

  const defaultSidebarOpen = cookieStore.get('sidebar_state')?.value !== 'false';

  return (
    <NewChatProvider>
      <AppShell defaultSidebarOpen={defaultSidebarOpen}>{children}</AppShell>
    </NewChatProvider>
  );
}
