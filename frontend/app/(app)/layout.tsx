import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { AppShell } from '@/components/app-shell';
import { authOptions } from '@/lib/auth';
import { NewChatProvider } from '@/lib/contexts/new-chat-context';

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect('/login');
  }

  const defaultSidebarOpen = (await cookies()).get('sidebar_state')?.value !== 'false';

  return (
    <NewChatProvider>
      <AppShell defaultSidebarOpen={defaultSidebarOpen}>{children}</AppShell>
    </NewChatProvider>
  );
}
