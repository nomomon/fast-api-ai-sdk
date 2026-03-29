const SettingsLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <main className="flex-1 overflow-auto">
      <div className="mx-auto max-w-7xl flex flex-col gap-8 p-4">
        <div className="flex items-center justify-between mt-12">
          <h1 className="text-2xl font-semibold">Settings</h1>
        </div>
        {children}
      </div>
    </main>
  );
};

export default SettingsLayout;
