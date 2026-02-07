import { Cable, Check, GlobeIcon, SearchIcon, X } from 'lucide-react';
import type React from 'react';
import { Shimmer } from '@/components/ai-elements/shimmer';

const toolIcons: Record<string, React.ReactNode> = {
  get_current_weather: <GlobeIcon className="h-4 w-4" />,
  update_skill: <Cable className="h-4 w-4" />,
  load_skill: <Cable className="h-4 w-4" />,
};

/**
 * Short, consistent gerund action labels (present participle),
 * 2-4 words, describing what the tool does in plain language.
 */
const toolDisplayNames: Record<string, string> = {
  get_current_weather: 'Checking the weather',
  update_skill: 'Updating a skill',
  load_skill: 'Loading a skill',
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
  const defaultIcon = <SearchIcon className="h-4 w-4" />;
  const icon: React.ReactNode =
    resolvedToolName in toolIcons ? toolIcons[resolvedToolName] : defaultIcon;

  // Get query/path from input for context
  const inputObj = input as Record<string, unknown> | undefined;
  const rawContext = inputObj?.query || inputObj?.path || inputObj?.pattern;
  const inputContext = rawContext ? String(rawContext) : null;

  if (state === 'output-available' || state === 'result') {
    return (
      <div className="text-sm text-muted-foreground flex items-center gap-2 mb-4">
        {icon}
        <span className="font-medium">{displayName}</span>
        {inputContext && (
          <span className="text-muted-foreground/50 truncate max-w-50">
            &ldquo;{inputContext}&rdquo;
          </span>
        )}
        <Check className="h-4 w-4 text-green-500 ml-.5" />
      </div>
    );
  }

  if (state === 'error' || state === 'failed') {
    return (
      <div className="text-sm text-muted-foreground flex items-center gap-2 mb-4">
        {icon}
        <span className="font-medium">{displayName}</span>
        {inputContext && (
          <span className="text-muted-foreground/50 truncate max-w-50">
            &ldquo;{inputContext}&rdquo;
          </span>
        )}
        <X className="h-4 w-4 text-red-500 ml-.5" />
      </div>
    );
  }

  // Pending/Running state
  return (
    <div className="text-sm text-muted-foreground flex items-center gap-2 mb-4">
      {icon}
      <Shimmer duration={1} className="font-medium">
        {displayName}
      </Shimmer>
      {inputContext && (
        <span className="text-muted-foreground/50 truncate max-w-50">
          &ldquo;{inputContext}&rdquo;
        </span>
      )}
    </div>
  );
}
