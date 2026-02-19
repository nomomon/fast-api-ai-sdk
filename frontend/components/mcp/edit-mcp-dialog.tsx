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

export interface EditMcpDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: () => void;
  formSubmitting: boolean;
  formProps: McpFormProps;
}

export function EditMcpDialog({
  open,
  onOpenChange,
  onSubmit,
  formSubmitting,
  formProps,
}: EditMcpDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit MCP</DialogTitle>
          <DialogDescription>Update name or configuration.</DialogDescription>
        </DialogHeader>
        <McpForm {...formProps} />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={formSubmitting}>
            {formSubmitting ? 'Saving…' : 'Save'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
