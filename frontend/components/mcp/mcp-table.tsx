import { PencilIcon, Trash2Icon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { Mcp } from '@/lib/interfaces/mcp';
import { StatusIndicator } from './status-indicator';
import { configSummary } from './utils';

export interface McpTableProps {
  mcps: Mcp[];
  checkingId: string | null;
  onCheck: (id: string) => void;
  onEdit: (mcp: Mcp) => void;
  onDelete: (id: string) => void;
}

export function McpTable({ mcps, checkingId, onCheck, onEdit, onDelete }: McpTableProps) {
  return (
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
                <TableCell className="max-w-lg truncate text-sm">
                  {configSummary(mcp.config)}
                </TableCell>
                <TableCell>
                  <StatusIndicator status={mcp.last_status} toolCount={mcp.last_tool_count} />
                </TableCell>
                <TableCell>{mcp.last_tool_count != null ? mcp.last_tool_count : '—'}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => onCheck(mcp.id)}
                      disabled={checkingId === mcp.id}
                      title="Test connection"
                    >
                      {checkingId === mcp.id ? '…' : 'Check'}
                    </Button>
                    <Button variant="ghost" size="icon-sm" onClick={() => onEdit(mcp)} title="Edit">
                      <PencilIcon className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => onDelete(mcp.id)}
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
  );
}
