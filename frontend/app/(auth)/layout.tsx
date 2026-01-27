import Image from 'next/image';
import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth/options';

export default async function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getServerSession(authOptions);

  if (session) {
    redirect('/');
  }

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <div className="flex items-center gap-2 font-medium">
            <Image
              src="/icons/app-icon.svg"
              alt="AI Chatbot"
              className="h-6 w-6 border-2 border-gray-200 rounded-sm"
              width={40}
              height={40}
            />
            AI Chatbot
          </div>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">{children}</div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        {/* Linear gradient using the primary color */}
        <div className="absolute inset-0 bg-linear-to-tr from-primary/10 to-primary/50" />
      </div>
    </div>
  );
}
