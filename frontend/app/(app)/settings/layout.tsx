import { SettingsShell } from '@/components/settings/settings-shell';

const SettingsLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <main className="flex-1 overflow-auto">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 p-4">
        <div className="mt-12 flex items-center justify-between">
          <h1 className="font-semibold text-2xl">Settings</h1>
        </div>
        <SettingsShell>{children}</SettingsShell>
      </div>
    </main>
  );
};

export default SettingsLayout;
