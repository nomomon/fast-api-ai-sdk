'use client';

import type { DataUIPart } from 'ai';
import {
  CheckCircle2Icon,
  FileTextIcon,
  GlobeIcon,
  Loader2Icon,
  type LucideIcon,
  SearchIcon,
} from 'lucide-react';
import type { ChatDataParts, WorkflowSearchData, WorkflowStatusData } from '@/types/chat';
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '../ai-elements/chain-of-thought';
import { Shimmer } from '../ai-elements/shimmer';

/** Maps workflow data types and phases to Lucide icons */
const WORKFLOW_ICONS: Record<string, LucideIcon> = {
  search: SearchIcon,
  status: FileTextIcon,
  'status:generating': Loader2Icon,
  'status:synthesizing': GlobeIcon,
  'status:analyzing': SearchIcon,
  'status:complete': CheckCircle2Icon,
};

type WorkflowIconResult = { icon: LucideIcon; iconClassName?: string };

function getWorkflowIcon(
  part: DataUIPart<ChatDataParts>,
  isStreaming?: boolean
): WorkflowIconResult {
  const type = part.type.replace('data-', '');
  if (type === 'status' && 'phase' in part.data) {
    const data = part.data as WorkflowStatusData;
    const icon = WORKFLOW_ICONS[`status:${data.phase}`] ?? WORKFLOW_ICONS.status;
    const iconClassName = data.phase === 'generating' && isStreaming ? 'animate-spin' : undefined;
    return { icon, iconClassName };
  }
  return { icon: WORKFLOW_ICONS[type] ?? WORKFLOW_ICONS.search };
}

function parseWebsiteHostname(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}

interface WorkflowPartProps {
  isStreaming: boolean;
  parts: Array<DataUIPart<ChatDataParts>>;
}

const defaultGetWorkflowHeaderMessage = (isStreaming: boolean) => {
  if (isStreaming) {
    return <Shimmer duration={1}>Researching...</Shimmer>;
  }
  return 'Research workflow';
};

export function WorkflowPart({ isStreaming, parts }: WorkflowPartProps) {
  if (parts.length === 0) return null;

  return (
    <ChainOfThought defaultOpen isStreaming={isStreaming}>
      <ChainOfThoughtHeader getHeaderMessage={defaultGetWorkflowHeaderMessage} />
      <ChainOfThoughtContent>
        {parts.map((part, index) => {
          const { icon: Icon, iconClassName } = getWorkflowIcon(part, isStreaming);

          if (part.type === 'data-search') {
            const data = part.data as WorkflowSearchData;
            const label = data.query
              ? `Search round ${data.round}: ${data.query}`
              : `Search round ${data.round}`;
            const status = data.status === 'active' ? 'active' : 'complete';

            return (
              <ChainOfThoughtStep
                key={`${part.type}-${data.round}-${index}`}
                icon={Icon}
                iconClassName={iconClassName}
                label={label}
                status={status}
              >
                {data.websites?.length ? (
                  <ChainOfThoughtSearchResults>
                    {data.websites.map((website) => (
                      <ChainOfThoughtSearchResult key={website}>
                        {parseWebsiteHostname(website)}
                      </ChainOfThoughtSearchResult>
                    ))}
                  </ChainOfThoughtSearchResults>
                ) : null}
              </ChainOfThoughtStep>
            );
          }

          if (part.type === 'data-status') {
            const data = part.data as WorkflowStatusData;
            const isGenerating = data.phase === 'generating' && isStreaming;
            const label = isGenerating ? (
              <Shimmer duration={1} key={`${part.type}-${index}-message`}>
                {data.message}
              </Shimmer>
            ) : (
              data.message
            );

            return (
              <ChainOfThoughtStep
                key={`${part.type}-${index}`}
                icon={Icon}
                iconClassName={iconClassName}
                label={label}
                status={isGenerating ? 'active' : 'complete'}
              />
            );
          }

          return null;
        })}
      </ChainOfThoughtContent>
    </ChainOfThought>
  );
}
