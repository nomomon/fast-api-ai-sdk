import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { McpFormProps } from './mcp-form';
import { McpForm } from './mcp-form';

export interface AddMcpDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: () => void;
  formSubmitting: boolean;
  formProps: McpFormProps;
}

export function AddMcpDialog({
  open,
  onOpenChange,
  onSubmit,
  formSubmitting,
  formProps,
}: AddMcpDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add MCP</DialogTitle>
          <DialogDescription>
            Add a Model Context Protocol server. Your chat agent will be able to use its tools.
          </DialogDescription>
        </DialogHeader>
        <McpForm {...formProps} />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={formSubmitting}>
            {formSubmitting ? 'Adding…' : 'Add'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
