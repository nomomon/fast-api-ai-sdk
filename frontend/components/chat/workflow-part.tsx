'use client';

import type { DataUIPart } from 'ai';
import { FileTextIcon, Loader2Icon, type LucideIcon, SearchIcon } from 'lucide-react';
import type {
  ChatDataParts,
  WorkflowEndLabelData,
  WorkflowStartLabelData,
  WorkflowStepData,
} from '@/types/chat';
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '../ai-elements/chain-of-thought';
import { Shimmer } from '../ai-elements/shimmer';

/** Icons for workflow step types. Only reachable: search, status. */
const STEP_ICONS: Record<string, LucideIcon> = {
  search: SearchIcon,
  status: FileTextIcon,
};

function getStepIcon(type?: string): LucideIcon {
  return STEP_ICONS[type ?? ''] ?? FileTextIcon;
}

interface WorkflowPartProps {
  isStreaming: boolean;
  parts: Array<DataUIPart<ChatDataParts>>;
}

function getWorkflowHeaderMessage(
  isStreaming: boolean,
  startLabel: WorkflowStartLabelData | null,
  endLabel: WorkflowEndLabelData | null
) {
  if (isStreaming && startLabel) {
    return <Shimmer duration={1}>{startLabel.label}</Shimmer>;
  }
  if (endLabel) {
    return endLabel.label;
  }
  return isStreaming ? 'Working...' : 'Workflow';
}

export function WorkflowPart({ isStreaming, parts }: WorkflowPartProps) {
  if (parts.length === 0) return null;

  const startLabelPart = parts.find((p) => p.type === 'data-start-label');
  const endLabelPart = parts.find((p) => p.type === 'data-end-label');
  const stepParts = parts.filter((p) => p.type === 'data-step');

  const startLabel = startLabelPart ? (startLabelPart.data as WorkflowStartLabelData) : null;
  const endLabel = endLabelPart ? (endLabelPart.data as WorkflowEndLabelData) : null;

  return (
    <ChainOfThought defaultOpen isStreaming={isStreaming}>
      <ChainOfThoughtHeader
        getHeaderMessage={() => getWorkflowHeaderMessage(isStreaming, startLabel, endLabel)}
      />
      <ChainOfThoughtContent>
        {stepParts.map((part, index) => {
          const data = part.data as WorkflowStepData;
          const isLast = index === stepParts.length - 1;
          const isLoading = isLast && isStreaming;

          const Icon = isLoading ? Loader2Icon : getStepIcon(data.type);
          const iconClassName = isLoading ? 'animate-spin' : undefined;
          const status = isLoading ? 'active' : 'complete';

          return (
            <ChainOfThoughtStep
              key={`${part.type}-${index}`}
              icon={Icon}
              iconClassName={iconClassName}
              label={data.label}
              status={status}
            >
              {data.details?.length ? (
                <ChainOfThoughtSearchResults>
                  {data.details.map((d) => (
                    <ChainOfThoughtSearchResult key={d}>{d}</ChainOfThoughtSearchResult>
                  ))}
                </ChainOfThoughtSearchResults>
              ) : null}
            </ChainOfThoughtStep>
          );
        })}
      </ChainOfThoughtContent>
    </ChainOfThought>
  );
}
