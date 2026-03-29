import { SettingsContent } from './settings-content';
import { SettingsSidebar } from './settings-sidebar';

const Settings = () => {
  return (
    <div className="flex min-h-0 w-full flex-1 flex-row">
      <SettingsSidebar />
      <SettingsContent title="General" />
    </div>
  );
};

export default Settings;
