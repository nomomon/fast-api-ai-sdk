import { SettingsContent } from '@/components/settings/settings-content';
import { SkillDashboard } from '@/components/skill';

export default function SkillsSettingsPage() {
  return (
    <SettingsContent
      title="Skills"
      description="Specialized instructions the agent can load to handle specific tasks."
      showPreferencesPlaceholder={false}
    >
      <SkillDashboard variant="settings" />
    </SettingsContent>
  );
}
