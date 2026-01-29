import type { DataUIPart } from 'ai';
import { SearchIcon } from 'lucide-react';
import type { ChatDataParts } from '@/types/chat';
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '../ai-elements/chain-of-thought';

interface WorkflowPartProps {
  isStreaming: boolean;
  parts: Array<DataUIPart<ChatDataParts>>;
}

// biome-ignore lint/correctness/noUnusedFunctionParameters: parts typed for future use when replacing placeholder UI
export function WorkflowPart({ isStreaming, parts }: WorkflowPartProps) {
  return (
    <ChainOfThought defaultOpen>
      <ChainOfThoughtHeader />
      <ChainOfThoughtContent>
        <ChainOfThoughtStep
          icon={SearchIcon}
          label="Searching for profiles for Hayden Bleasel"
          status="complete"
        >
          <ChainOfThoughtSearchResults>
            {['https://www.x.com', 'https://www.instagram.com', 'https://www.github.com'].map(
              (website) => (
                <ChainOfThoughtSearchResult key={website}>
                  {new URL(website).hostname}
                </ChainOfThoughtSearchResult>
              )
            )}
          </ChainOfThoughtSearchResults>
        </ChainOfThoughtStep>

        <ChainOfThoughtStep
          label="Hayden Bleasel is an Australian product designer, software engineer, and founder. He is currently based in the United States working for Vercel, an American cloud application company."
          status="complete"
        />

        <ChainOfThoughtStep icon={SearchIcon} label="Searching for recent work..." status="active">
          <ChainOfThoughtSearchResults>
            {['https://www.github.com', 'https://www.dribbble.com'].map((website) => (
              <ChainOfThoughtSearchResult key={website}>
                {new URL(website).hostname}
              </ChainOfThoughtSearchResult>
            ))}
          </ChainOfThoughtSearchResults>
        </ChainOfThoughtStep>
      </ChainOfThoughtContent>
    </ChainOfThought>
  );
}
