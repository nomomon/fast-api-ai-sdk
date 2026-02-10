export type McpTransport = 'stdio' | 'streamable-http';

export interface McpConfigStdio {
  transport: 'stdio';
  command: string;
  args: string[];
  env?: Record<string, string>;
}

export interface McpConfigStreamableHttp {
  transport: 'streamable-http';
  url: string;
  api_key?: string;
  headers?: Record<string, string>;
}

export type McpConfig = McpConfigStdio | McpConfigStreamableHttp;

export interface Mcp {
  id: string;
  name: string;
  config: McpConfig;
  last_status: string | null;
  last_tool_count: number | null;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface McpCreateBody {
  name: string;
  config: McpConfig;
}

export interface McpUpdateBody {
  name?: string;
  config?: McpConfig;
}
