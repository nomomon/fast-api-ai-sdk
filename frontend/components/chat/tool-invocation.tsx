import { GlobeIcon, SearchIcon } from 'lucide-react';
import type React from 'react';

const toolIcons: Record<string, React.ReactNode> = {
  get_current_weather: <GlobeIcon className="h-3 w-3" />,
};

const toolDisplayNames: Record<string, string> = {
  get_current_weather: 'Getting weather',
};

export function ToolInvocation({
  toolType,
  toolName,
  state,
  input,
}: {
  toolType: string;
  toolName?: string;
  state?: string;
  input?: unknown;
}) {
  // Extract tool name from type (e.g., "tool-searchChromium" -> "searchChromium")
  const resolvedToolName = toolName || toolType.replace('tool-', '');
  const displayName = toolDisplayNames[resolvedToolName] || resolvedToolName;
  const defaultIcon = <SearchIcon className="h-3 w-3" />;
  const icon: React.ReactNode =
    resolvedToolName in toolIcons ? toolIcons[resolvedToolName] : defaultIcon;

  // Get query/path from input for context
  const inputObj = input as Record<string, unknown> | undefined;
  const rawContext = inputObj?.query || inputObj?.path || inputObj?.pattern;
  const inputContext = rawContext ? String(rawContext) : null;

  if (state === 'output-available' || state === 'result') {
    return (
      <div className="text-xs text-muted-foreground/70 flex items-center gap-1.5 py-1.5 px-2 bg-muted/30 rounded-lg my-1">
        {icon}
        <span className="font-medium">{displayName}</span>
        {inputContext && (
          <span className="text-muted-foreground/50 truncate max-w-50">
            &ldquo;{inputContext}&rdquo;
          </span>
        )}
        <span className="text-green-500 ml-auto">✓</span>
      </div>
    );
  }

  // Pending/Running state
  return (
    <div className="text-xs text-muted-foreground/70 flex items-center gap-1.5 py-1.5 px-2 bg-muted/30 rounded-lg my-1 animate-pulse">
      {icon}
      <span className="font-medium">{displayName}</span>
      {inputContext && (
        <span className="text-muted-foreground/50 truncate max-w-50">
          &ldquo;{inputContext}&rdquo;
        </span>
      )}
      <span className="ml-auto">...</span>
    </div>
  );
}
