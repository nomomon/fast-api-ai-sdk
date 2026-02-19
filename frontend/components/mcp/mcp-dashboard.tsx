'use client';

import { PlusIcon } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useMcps } from '@/lib/hooks/use-mcps';
import type { Mcp, McpConfig, McpConfigStreamableHttp } from '@/lib/interfaces/mcp';
import { AddMcpDialog } from './add-mcp-dialog';
import { DeleteMcpDialog } from './delete-mcp-dialog';
import { EditMcpDialog } from './edit-mcp-dialog';
import { McpTable } from './mcp-table';

export function McpDashboard() {
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
  const [formApiKey, setFormApiKey] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [checkingId, setCheckingId] = useState<string | null>(null);

  const resetForm = () => {
    setFormName('');
    setFormTransport('streamable-http');
    setFormCommand('');
    setFormArgs('');
    setFormUrl('');
    setFormApiKey('');
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
      setFormApiKey(mcp.config.api_key ?? '');
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
    const streamable: McpConfig = {
      transport: 'streamable-http',
      url: formUrl.trim(),
    };
    if (formApiKey.trim()) {
      (streamable as McpConfigStreamableHttp).api_key = formApiKey.trim();
    }
    return streamable;
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

  const formProps = {
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
  };

  return (
    <>
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
          <McpTable
            mcps={mcps}
            checkingId={checkingId}
            onCheck={handleCheck}
            onEdit={openEdit}
            onDelete={setDeleteId}
          />
        )}
      </section>

      <AddMcpDialog
        open={addOpen}
        onOpenChange={setAddOpen}
        onSubmit={handleAdd}
        formSubmitting={formSubmitting}
        formProps={formProps}
      />

      <EditMcpDialog
        open={!!editMcp}
        onOpenChange={(open) => !open && closeEdit()}
        onSubmit={handleEdit}
        formSubmitting={formSubmitting}
        formProps={formProps}
      />

      <DeleteMcpDialog
        mcpId={deleteId}
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </>
  );
}
