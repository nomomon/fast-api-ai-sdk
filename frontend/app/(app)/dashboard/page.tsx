'use client';

import { Pencil, Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Sheet, SheetContent, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Textarea } from '@/components/ui/textarea';
import { deleteSkill, updateSkill, useUserSkills } from '@/lib/hooks/use-user-skills';
import type { UserSkill } from '@/lib/interfaces/user-skill';

function SkillCard({
  skill,
  onEdit,
  onDelete,
}: {
  skill: UserSkill;
  onEdit: (skill: UserSkill) => void;
  onDelete: (skill: UserSkill) => void;
}) {
  const handleDelete = () => {
    if (window.confirm(`Delete skill "${skill.name}"?`)) {
      onDelete(skill);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{skill.name}</CardTitle>
        <CardAction className="flex gap-2">
          <Button variant="outline" size="icon-sm" onClick={() => onEdit(skill)} aria-label="Edit">
            <Pencil className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={handleDelete}
            aria-label="Delete"
            className="text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="size-4" />
          </Button>
        </CardAction>
        {skill.description ? <CardDescription>{skill.description}</CardDescription> : null}
      </CardHeader>
      <CardContent>
        <pre className="overflow-auto rounded-md border bg-muted p-4 font-mono text-sm">
          <code className="block whitespace-pre">{skill.content || '(empty)'}</code>
        </pre>
      </CardContent>
    </Card>
  );
}

function EditSkillSheet({
  skill,
  open,
  onOpenChange,
  onSaved,
}: {
  skill: UserSkill | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}) {
  const [description, setDescription] = useState('');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (skill && open) {
      setDescription(skill.description);
      setContent(skill.content);
    }
  }, [skill, open]);

  const resetForm = () => {
    setDescription('');
    setContent('');
  };

  const handleOpenChange = (next: boolean) => {
    if (!next) resetForm();
    onOpenChange(next);
  };

  const handleSave = async () => {
    if (!skill) return;
    setSaving(true);
    try {
      await updateSkill(skill.id, { description, content });
      toast.success('Skill updated');
      handleOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to update skill');
    } finally {
      setSaving(false);
    }
  };

  if (!skill) return null;

  return (
    <Sheet open={open} onOpenChange={handleOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col overflow-hidden sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>Edit skill: {skill.name}</SheetTitle>
        </SheetHeader>
        <div className="flex flex-1 flex-col gap-4 overflow-y-auto py-4">
          <div className="grid gap-2">
            <Label htmlFor="edit-description">Description</Label>
            <Textarea
              id="edit-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What the skill does, when to use it"
              rows={2}
              className="resize-none font-mono text-sm"
            />
          </div>
          <div className="grid flex-1 gap-2">
            <Label htmlFor="edit-content">Content (markdown)</Label>
            <Textarea
              id="edit-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Skill body content..."
              className="min-h-[200px] resize-y font-mono text-sm"
            />
          </div>
        </div>
        <SheetFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

export default function DashboardPage() {
  const { skills, isLoading, error, refetch } = useUserSkills();
  const [editingSkill, setEditingSkill] = useState<UserSkill | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  const handleEdit = (skill: UserSkill) => {
    setEditingSkill(skill);
    setSheetOpen(true);
  };

  const handleDelete = async (skill: UserSkill) => {
    try {
      await deleteSkill(skill.id);
      toast.success('Skill deleted');
      refetch();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to delete skill');
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4 p-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p className="text-muted-foreground">Your user skills. Edit or delete from here.</p>

      {isLoading ? (
        <p className="text-muted-foreground">Loading skills…</p>
      ) : error ? (
        <p className="text-destructive">{error.message}</p>
      ) : skills.length === 0 ? (
        <p className="text-muted-foreground">You have no user skills yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {skills.map((skill) => (
            <SkillCard key={skill.id} skill={skill} onEdit={handleEdit} onDelete={handleDelete} />
          ))}
        </div>
      )}

      <EditSkillSheet
        skill={editingSkill}
        open={sheetOpen}
        onOpenChange={(open) => {
          setSheetOpen(open);
          if (!open) setEditingSkill(null);
        }}
        onSaved={refetch}
      />
    </div>
  );
}
