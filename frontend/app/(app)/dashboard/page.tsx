import Link from 'next/link';

export default function DashboardPage() {
  return (
    <main className="flex-1 overflow-auto">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 p-4">
        <div className="mt-12 flex items-center justify-between">
          <h1 className="font-semibold text-2xl">Dashboard</h1>
        </div>
        <p className="text-muted-foreground text-sm leading-relaxed">
          Welcome. Manage skills and MCP connections in{' '}
          <Link href="/settings" className="text-foreground underline underline-offset-4">
            Settings
          </Link>
          :{' '}
          <Link href="/settings/skills" className="text-foreground underline underline-offset-4">
            Skills
          </Link>{' '}
          and{' '}
          <Link href="/settings/tools" className="text-foreground underline underline-offset-4">
            Tools & MCPs
          </Link>
          .
        </p>
      </div>
    </main>
  );
}
