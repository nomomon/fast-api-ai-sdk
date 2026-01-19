import { ListChecks } from 'lucide-react';

export default async function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  //   const session = await getServerSession(authOptions);

  //   if (session) {
  //     redirect('/');
  //   }

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <div className="flex items-center gap-2 font-medium">
            <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <ListChecks className="size-4" />
            </div>
            todo app
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
