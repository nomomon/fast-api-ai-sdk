import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { SkillFormProps } from './skill-form';
import { SkillForm } from './skill-form';

export interface EditSkillDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: () => void;
  formSubmitting: boolean;
  formProps: SkillFormProps;
}

export function EditSkillDialog({
  open,
  onOpenChange,
  onSubmit,
  formSubmitting,
  formProps,
}: EditSkillDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-4xl">
        <DialogHeader>
          <DialogTitle>Edit Skill</DialogTitle>
          <DialogDescription>Update the skill name, description, or content.</DialogDescription>
        </DialogHeader>
        <SkillForm {...formProps} />
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
