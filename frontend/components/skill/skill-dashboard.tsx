'use client';

import { PlusIcon } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useSkills } from '@/lib/hooks/use-skills';
import type { Skill } from '@/lib/interfaces/skill';
import { AddSkillDialog } from './add-skill-dialog';
import { DeleteSkillDialog } from './delete-skill-dialog';
import { EditSkillDialog } from './edit-skill-dialog';
import { SkillTable } from './skill-table';

export function SkillDashboard() {
  const { skills, loading, error, createSkill, updateSkill, deleteSkill } = useSkills();
  const [addOpen, setAddOpen] = useState(false);
  const [editSkill, setEditSkill] = useState<Skill | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteName, setDeleteName] = useState<string | null>(null);
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const resetForm = () => {
    setFormName('');
    setFormDescription('');
    setFormContent('');
    setFormError(null);
  };

  const openAdd = () => {
    resetForm();
    setAddOpen(true);
  };

  const openEdit = (skill: Skill) => {
    setFormName(skill.name);
    setFormDescription(skill.description);
    setFormContent(skill.content);
    setEditSkill(skill);
    setFormError(null);
  };

  const closeEdit = () => {
    setEditSkill(null);
    resetForm();
  };

  const openDelete = (skill: Skill) => {
    setDeleteId(skill.id);
    setDeleteName(skill.name);
  };

  const handleAdd = async () => {
    setFormSubmitting(true);
    setFormError(null);
    try {
      if (!formName.trim()) {
        setFormError('Name is required');
        return;
      }
      await createSkill({
        name: formName.trim(),
        description: formDescription.trim(),
        content: formContent.trim(),
      });
      setAddOpen(false);
      resetForm();
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to create');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleEdit = async () => {
    if (!editSkill) return;
    setFormSubmitting(true);
    setFormError(null);
    try {
      if (!formName.trim()) {
        setFormError('Name is required');
        return;
      }
      await updateSkill(editSkill.id, {
        name: formName.trim(),
        description: formDescription.trim(),
        content: formContent.trim(),
      });
      closeEdit();
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to update');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDelete = async (skillId: string) => {
    try {
      await deleteSkill(skillId);
      setDeleteId(null);
      setDeleteName(null);
    } catch {
      // could toast
    }
  };

  const formProps = {
    formName,
    setFormName,
    formDescription,
    setFormDescription,
    formContent,
    setFormContent,
    formError,
  };

  return (
    <>
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium">Your Skills</h2>
          <Button onClick={openAdd} size="sm">
            <PlusIcon className="size-4" />
            Add Skill
          </Button>
        </div>

        {error && (
          <p className="text-destructive text-sm" role="alert">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-muted-foreground text-sm">Loading skills…</p>
        ) : (
          <SkillTable skills={skills} onEdit={openEdit} onDelete={openDelete} />
        )}
      </section>

      <AddSkillDialog
        open={addOpen}
        onOpenChange={setAddOpen}
        onSubmit={handleAdd}
        formSubmitting={formSubmitting}
        formProps={formProps}
      />

      <EditSkillDialog
        open={!!editSkill}
        onOpenChange={(open) => !open && closeEdit()}
        onSubmit={handleEdit}
        formSubmitting={formSubmitting}
        formProps={formProps}
      />

      <DeleteSkillDialog
        skillId={deleteId}
        skillName={deleteName}
        open={!!deleteId}
        onOpenChange={(open) => {
          if (!open) {
            setDeleteId(null);
            setDeleteName(null);
          }
        }}
        onConfirm={(id) => handleDelete(id)}
      />
    </>
  );
}
