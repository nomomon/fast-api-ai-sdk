import type { DynamicToolUIPart } from 'ai';
import { Cable, Check, GlobeIcon, Loader2, SearchIcon, X } from 'lucide-react';
import type { FC } from 'react';
import { Shimmer } from '@/components/ai-elements/shimmer';

export type ToolInvocationState = DynamicToolUIPart['state'];

export interface ToolInvocationProps {
  toolType?: string;
  state: ToolInvocationState;
  input?: unknown;
}

interface ToolConfig {
  icon: React.ReactNode;
  displayName: string;
  inputContext: (input: unknown) => string;
}

const PENDING_STATES: ToolInvocationState[] = [
  'input-streaming',
  'input-available',
  'approval-requested',
  'approval-responded',
];

const getStateIcon = (state: ToolInvocationState): React.ReactNode =>
  PENDING_STATES.includes(state) ? (
    <Loader2 className="h-4 w-4 text-gray-500 ml-.5 animate-spin" />
  ) : state === 'output-available' ? (
    <Check className="h-4 w-4 text-green-500 ml-.5" />
  ) : (
    <X className="h-4 w-4 text-red-500 ml-.5" />
  );

/** Returns a function that reads a string from tool input at the given key. */
const inputContextFrom =
  (key: string) =>
  (input: unknown): string => {
    if (input == null || typeof input !== 'object') return '';
    const raw = (input as Record<string, unknown>)[key];
    return raw != null ? String(raw) : '';
  };

const DEFAULT_CONFIG: ToolConfig = {
  icon: <SearchIcon className="h-4 w-4" />,
  displayName: 'Tool',
  inputContext: () => '',
};

const TOOL_CONFIG: Record<string, Partial<ToolConfig>> = {
  get_current_weather: {
    displayName: 'Checking the weather',
    icon: <GlobeIcon className="h-4 w-4" />,
  },
  update_skill: {
    displayName: 'Updating a skill',
    icon: <Cable className="h-4 w-4" />,
    inputContext: inputContextFrom('skill_name'),
  },
  load_skill: {
    displayName: 'Loading a skill',
    icon: <Cable className="h-4 w-4" />,
    inputContext: inputContextFrom('skill_name'),
  },
};

const ToolDisplay: FC<{
  config: ToolConfig;
  input?: unknown;
  state: ToolInvocationState;
}> = ({ config, input, state }) => {
  const { icon, displayName, inputContext } = config;
  const contextText = inputContext(input);
  const pending = PENDING_STATES.includes(state);

  return (
    <div
      className="text-sm text-muted-foreground flex items-center gap-2 mb-4"
      {...(pending && { role: 'status' as const, 'aria-live': 'polite' as const })}
    >
      {icon}
      {pending ? (
        <Shimmer duration={1} className="font-medium">
          {displayName}
        </Shimmer>
      ) : (
        <span className="font-medium">{displayName}</span>
      )}
      {contextText ? (
        <span className="text-muted-foreground/50 truncate max-w-50">
          &ldquo;{contextText}&rdquo;
        </span>
      ) : null}
      {getStateIcon(state)}
    </div>
  );
};

export function ToolInvocation({ toolType, state, input }: ToolInvocationProps) {
  const resolvedName = toolType?.replace(/^tool-/, '') || 'unknown';
  const overrides = TOOL_CONFIG[resolvedName];
  const config: ToolConfig = {
    ...DEFAULT_CONFIG,
    ...overrides,
    displayName: overrides?.displayName ?? resolvedName,
  };

  return <ToolDisplay config={config} input={input} state={state} />;
}
