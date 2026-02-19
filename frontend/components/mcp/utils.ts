import type { McpConfig } from '@/lib/interfaces/mcp';

export function configSummary(config: McpConfig): string {
  if (config.transport === 'stdio') {
    const parts = [config.command, ...(config.args || [])];
    return `stdio: ${parts.join(' ')}`;
  }
  return `HTTP: ${config.url}`;
}
