import type { UIMessage } from 'ai';

/**
 * Extracts the message content as markdown from UIMessage parts.
 * Includes text parts and reasoning parts (prefixed as blockquote).
 */
export function getMessageMarkdown(message: UIMessage): string {
  const sections: string[] = [];

  for (const part of message.parts) {
    if (part.type === 'text' && part.text) {
      sections.push(part.text);
    }
    if (part.type === 'reasoning' && part.text) {
      sections.push(`> _Reasoning:_\n> ${part.text.replace(/\n/g, '\n> ')}`);
    }
  }

  return sections.join('\n\n').trim();
}

/**
 * Extracts plain text from a user message (text parts only).
 */
export function getUserMessageText(message: UIMessage): string {
  return message.parts
    .filter(
      (part): part is { type: 'text'; text: string } => part.type === 'text' && 'text' in part
    )
    .map((part) => part.text)
    .join('');
}
