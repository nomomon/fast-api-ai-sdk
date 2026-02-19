export function StatusIndicator({
  status,
  toolCount,
}: {
  status: string | null;
  toolCount: number | null;
}) {
  if (status === 'ok') {
    return (
      <span className="inline-flex items-center gap-1.5 text-green-600 dark:text-green-500">
        <span className="size-2 rounded-full bg-green-500" aria-hidden />
        OK {toolCount != null ? `(${toolCount} tools)` : ''}
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="inline-flex items-center gap-1.5 text-destructive">
        <span className="size-2 rounded-full bg-destructive" aria-hidden />
        Error
      </span>
    );
  }
  return (
    <span className="text-muted-foreground">
      — <span className="sr-only">Not checked</span>
    </span>
  );
}
