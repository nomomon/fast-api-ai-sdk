import type { DataUIPart, UIDataTypes } from 'ai';
import { SearchIcon } from 'lucide-react';
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '../ai-elements/chain-of-thought';

interface WorkflowProcessProps {
  isStreaming: boolean;
  parts: unknown[];
}

export function WorkflowProcess({ isStreaming, parts }: WorkflowProcessProps) {
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
