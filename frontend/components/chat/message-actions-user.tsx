'use client';

import { Pencil } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface UserMessageActionsProps {
  onEditClick: () => void;
}

export function UserMessageActions({ onEditClick }: UserMessageActionsProps) {
  return (
    <div className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity shrink-0">
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onEditClick}
        aria-label="Edit message"
        className="text-muted-foreground hover:text-foreground"
      >
        <Pencil className="h-4 w-4" />
      </Button>
    </div>
  );
}
