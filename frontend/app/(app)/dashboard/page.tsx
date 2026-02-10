'use client';

import { PencilIcon, PlusIcon, Trash2Icon } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useMcps } from '@/lib/hooks/use-mcps';
import type { Mcp, McpConfig } from '@/lib/interfaces/mcp';

function configSummary(config: McpConfig): string {
  if (config.transport === 'stdio') {
    const parts = [config.command, ...(config.args || [])];
    return `stdio: ${parts.join(' ')}`;
  }
  return `HTTP: ${config.url}`;
}

function StatusIndicator({
  status,
  toolCount,
}: {
  status: string | null;
  toolCount: number | null;
}) {
  if (status === 'ok') {
    return (
      <span className="inline-flex items-center gap-1.5 text-green-600 dark:text-green-500">
        <span className="size-2 rounded-full bg-green-500" aria-hidden />
        OK {toolCount != null ? `(${toolCount} tools)` : ''}
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="inline-flex items-center gap-1.5 text-destructive">
        <span className="size-2 rounded-full bg-destructive" aria-hidden />
        Error
      </span>
    );
  }
  return (
    <span className="text-muted-foreground">
      — <span className="sr-only">Not checked</span>
    </span>
  );
}

export default function DashboardPage() {
  const { mcps, loading, error, createMcp, updateMcp, deleteMcp, checkMcp } = useMcps();
  const [addOpen, setAddOpen] = useState(false);
  const [editMcp, setEditMcp] = useState<Mcp | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [formName, setFormName] = useState('');
  const [formTransport, setFormTransport] = useState<'stdio' | 'streamable-http'>(
    'streamable-http'
  );
  const [formCommand, setFormCommand] = useState('');
  const [formArgs, setFormArgs] = useState('');
  const [formUrl, setFormUrl] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [checkingId, setCheckingId] = useState<string | null>(null);

  const resetForm = () => {
    setFormName('');
    setFormTransport('streamable-http');
    setFormCommand('');
    setFormArgs('');
    setFormUrl('');
    setFormError(null);
  };

  const openAdd = () => {
    resetForm();
    setAddOpen(true);
  };

  const openEdit = (mcp: Mcp) => {
    setFormName(mcp.name);
    setFormTransport(mcp.config.transport);
    if (mcp.config.transport === 'stdio') {
      setFormCommand(mcp.config.command);
      setFormArgs((mcp.config.args || []).join(' '));
      setFormUrl('');
    } else {
      setFormUrl(mcp.config.url);
      setFormCommand('');
      setFormArgs('');
    }
    setEditMcp(mcp);
    setFormError(null);
  };

  const closeEdit = () => {
    setEditMcp(null);
    resetForm();
  };

  const buildConfig = (): McpConfig => {
    if (formTransport === 'stdio') {
      const args = formArgs.trim() ? formArgs.trim().split(/\s+/).filter(Boolean) : [];
      return { transport: 'stdio', command: formCommand.trim(), args };
    }
    return { transport: 'streamable-http', url: formUrl.trim() };
  };

  const handleAdd = async () => {
    setFormSubmitting(true);
    setFormError(null);
    try {
      const config = buildConfig();
      if (formTransport === 'stdio' && !formCommand.trim()) {
        setFormError('Command is required');
        return;
      }
      if (formTransport === 'streamable-http' && !formUrl.trim()) {
        setFormError('URL is required');
        return;
      }
      if (!formName.trim()) {
        setFormError('Name is required');
        return;
      }
      await createMcp({ name: formName.trim(), config });
      setAddOpen(false);
      resetForm();
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to create');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleEdit = async () => {
    if (!editMcp) return;
    setFormSubmitting(true);
    setFormError(null);
    try {
      const config = buildConfig();
      if (formTransport === 'stdio' && !formCommand.trim()) {
        setFormError('Command is required');
        return;
      }
      if (formTransport === 'streamable-http' && !formUrl.trim()) {
        setFormError('URL is required');
        return;
      }
      if (!formName.trim()) {
        setFormError('Name is required');
        return;
      }
      await updateMcp(editMcp.id, { name: formName.trim(), config });
      closeEdit();
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to update');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMcp(id);
      setDeleteId(null);
    } catch {
      // could toast
    }
  };

  const handleCheck = async (id: string) => {
    setCheckingId(id);
    try {
      await checkMcp(id);
    } finally {
      setCheckingId(null);
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium">Your MCPs</h2>
          <Button onClick={openAdd} size="sm">
            <PlusIcon className="size-4" />
            Add MCP
          </Button>
        </div>

        {error && (
          <p className="text-destructive text-sm" role="alert">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-muted-foreground text-sm">Loading MCPs…</p>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Config</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Tools</TableHead>
                  <TableHead className="w-[120px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mcps.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-muted-foreground text-center">
                      No MCPs yet. Add one to connect your agent to external tools.
                    </TableCell>
                  </TableRow>
                ) : (
                  mcps.map((mcp) => (
                    <TableRow key={mcp.id}>
                      <TableCell className="font-medium">{mcp.name}</TableCell>
                      <TableCell className="max-w-[200px] truncate text-sm">
                        {configSummary(mcp.config)}
                      </TableCell>
                      <TableCell>
                        <StatusIndicator status={mcp.last_status} toolCount={mcp.last_tool_count} />
                      </TableCell>
                      <TableCell>
                        {mcp.last_tool_count != null ? mcp.last_tool_count : '—'}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => handleCheck(mcp.id)}
                            disabled={checkingId === mcp.id}
                            title="Test connection"
                          >
                            {checkingId === mcp.id ? '…' : 'Check'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => openEdit(mcp)}
                            title="Edit"
                          >
                            <PencilIcon className="size-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => setDeleteId(mcp.id)}
                            title="Delete"
                          >
                            <Trash2Icon className="size-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </section>

      {/* Add MCP Dialog */}
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add MCP</DialogTitle>
            <DialogDescription>
              Add a Model Context Protocol server. Your chat agent will be able to use its tools.
            </DialogDescription>
          </DialogHeader>
          <McpForm
            formName={formName}
            setFormName={setFormName}
            formTransport={formTransport}
            setFormTransport={setFormTransport}
            formCommand={formCommand}
            setFormCommand={setFormCommand}
            formArgs={formArgs}
            setFormArgs={setFormArgs}
            formUrl={formUrl}
            setFormUrl={setFormUrl}
            formError={formError}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAdd} disabled={formSubmitting}>
              {formSubmitting ? 'Adding…' : 'Add'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit MCP Dialog */}
      <Dialog open={!!editMcp} onOpenChange={(open) => !open && closeEdit()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Edit MCP</DialogTitle>
            <DialogDescription>Update name or configuration.</DialogDescription>
          </DialogHeader>
          <McpForm
            formName={formName}
            setFormName={setFormName}
            formTransport={formTransport}
            setFormTransport={setFormTransport}
            formCommand={formCommand}
            setFormCommand={setFormCommand}
            formArgs={formArgs}
            setFormArgs={setFormArgs}
            formUrl={formUrl}
            setFormUrl={setFormUrl}
            formError={formError}
          />
          <DialogFooter>
            <Button variant="outline" onClick={closeEdit}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={formSubmitting}>
              {formSubmitting ? 'Saving…' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Delete MCP</DialogTitle>
            <DialogDescription>
              Remove this MCP? Your agent will no longer use its tools.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteId && handleDelete(deleteId)}
              disabled={!deleteId}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function McpForm({
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
  formError,
}: {
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
  formError: string | null;
}) {
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
      )}
    </div>
  );
}
