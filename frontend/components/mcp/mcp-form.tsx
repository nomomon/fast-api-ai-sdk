import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface McpFormProps {
  formName: string;
  setFormName: (v: string) => void;
  formTransport: 'stdio' | 'streamable-http';
  setFormTransport: (v: 'stdio' | 'streamable-http') => void;
  formCommand: string;
  setFormCommand: (v: string) => void;
  formArgs: string;
  setFormArgs: (v: string) => void;
  formUrl: string;
  setFormUrl: (v: string) => void;
  formApiKey: string;
  setFormApiKey: (v: string) => void;
  formError: string | null;
}

export function McpForm({
  formName,
  setFormName,
  formTransport,
  setFormTransport,
  formCommand,
  setFormCommand,
  formArgs,
  setFormArgs,
  formUrl,
  setFormUrl,
  formApiKey,
  setFormApiKey,
  formError,
}: McpFormProps) {
  return (
    <div className="grid gap-4 py-4">
      {formError && (
        <p className="text-destructive text-sm" role="alert">
          {formError}
        </p>
      )}
      <div className="grid gap-2">
        <Label htmlFor="mcp-name">Name</Label>
        <Input
          id="mcp-name"
          value={formName}
          onChange={(e) => setFormName(e.target.value)}
          placeholder="e.g. Brave Search"
        />
      </div>
      <div className="grid gap-2">
        <Label>Transport</Label>
        <Select
          value={formTransport}
          onValueChange={(v) => setFormTransport(v as 'stdio' | 'streamable-http')}
        >
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="streamable-http">Streamable HTTP (URL)</SelectItem>
            <SelectItem value="stdio">Stdio (command)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {formTransport === 'stdio' ? (
        <>
          <div className="grid gap-2">
            <Label htmlFor="mcp-command">Command</Label>
            <Input
              id="mcp-command"
              value={formCommand}
              onChange={(e) => setFormCommand(e.target.value)}
              placeholder="e.g. npx"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="mcp-args">Arguments (space-separated)</Label>
            <Input
              id="mcp-args"
              value={formArgs}
              onChange={(e) => setFormArgs(e.target.value)}
              placeholder="e.g. -y @modelcontextprotocol/server-brave-search"
            />
          </div>
        </>
      ) : (
        <>
          <div className="grid gap-2">
            <Label htmlFor="mcp-url">URL</Label>
            <Input
              id="mcp-url"
              type="url"
              value={formUrl}
              onChange={(e) => setFormUrl(e.target.value)}
              placeholder="https://example.com/mcp"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="mcp-api-key">API key (optional)</Label>
            <Input
              id="mcp-api-key"
              type="password"
              value={formApiKey}
              onChange={(e) => setFormApiKey(e.target.value)}
              placeholder="Optional"
              autoComplete="off"
            />
          </div>
        </>
      )}
    </div>
  );
}
