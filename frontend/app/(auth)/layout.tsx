import { cookies } from 'next/headers';
import Image from 'next/image';
import { redirect } from 'next/navigation';
import { AUTH_COOKIE_NAME } from '@/lib/auth/constants';
import { ICON_PATHS } from '@/lib/constants/seo';

export default async function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;
  if (token) {
    redirect('/');
  }

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <div className="flex items-center gap-2 font-medium">
            <Image
              src={ICON_PATHS.svg}
              alt="AI Chatbot"
              className="h-6 w-6 border-2 border-gray-200 rounded-sm"
              width={40}
              height={40}
            />
            AI Chatbot
          </div>
        </div>
        <main className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">{children}</div>
        </main>
      </div>
      <div className="bg-muted relative hidden lg:block">
        {/* Linear gradient using the primary color */}
        <div className="absolute inset-0 bg-linear-to-tr from-primary/10 to-primary/50" />
      </div>
    </div>
  );
}
