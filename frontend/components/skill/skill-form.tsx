import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export interface SkillFormProps {
  formName: string;
  setFormName: (v: string) => void;
  formDescription: string;
  setFormDescription: (v: string) => void;
  formContent: string;
  setFormContent: (v: string) => void;
  formError: string | null;
}

export function SkillForm({
  formName,
  setFormName,
  formDescription,
  setFormDescription,
  formContent,
  setFormContent,
  formError,
}: SkillFormProps) {
  return (
    <div className="grid gap-4 py-4">
      {formError && (
        <p className="text-destructive text-sm" role="alert">
          {formError}
        </p>
      )}
      <div className="grid gap-2">
        <Label htmlFor="skill-name">Name</Label>
        <Input
          id="skill-name"
          value={formName}
          onChange={(e) => setFormName(e.target.value)}
          placeholder="e.g. my-skill"
        />
        <p className="text-muted-foreground text-xs">
          Lowercase letters, numbers, hyphens only (e.g. my-skill).
        </p>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="skill-description">Description</Label>
        <Textarea
          id="skill-description"
          value={formDescription}
          onChange={(e) => setFormDescription(e.target.value)}
          placeholder="What the skill does and when to use it"
          rows={2}
          className="min-h-15"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="skill-content">Content (instructions)</Label>
        <Textarea
          id="skill-content"
          value={formContent}
          onChange={(e) => setFormContent(e.target.value)}
          placeholder="Markdown instructions for the agent"
          className="min-h-50 font-mono text-sm"
        />
      </div>
    </div>
  );
}
