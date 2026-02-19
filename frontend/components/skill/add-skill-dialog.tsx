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

export interface AddSkillDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: () => void;
  formSubmitting: boolean;
  formProps: SkillFormProps;
}

export function AddSkillDialog({
  open,
  onOpenChange,
  onSubmit,
  formSubmitting,
  formProps,
}: AddSkillDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-4xl">
        <DialogHeader>
          <DialogTitle>Add Skill</DialogTitle>
          <DialogDescription>
            Create a custom skill. Your agent will load it when relevant.
          </DialogDescription>
        </DialogHeader>
        <SkillForm {...formProps} />
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
