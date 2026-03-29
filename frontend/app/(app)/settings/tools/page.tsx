import { McpDashboard } from '@/components/mcp';
import { SettingsContent } from '@/components/settings/settings-content';

export default function ToolsSettingsPage() {
  return (
    <SettingsContent
      title="Tools & MCPs"
      description="Connect the agent to external tools via Model Context Protocol servers."
      showPreferencesPlaceholder={false}
    >
      <McpDashboard variant="settings" />
    </SettingsContent>
  );
}
