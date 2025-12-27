'use client';

import {
    Conversation,
    ConversationContent,
    ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import {
    PromptInput,
    PromptInputActionAddAttachments,
    PromptInputActionMenu,
    PromptInputActionMenuContent,
    PromptInputActionMenuTrigger,
    PromptInputAttachment,
    PromptInputAttachments,
    PromptInputBody,
    PromptInputButton,
    PromptInputHeader,
    type PromptInputMessage,
    PromptInputSelect,
    PromptInputSelectContent,
    PromptInputSelectItem,
    PromptInputSelectTrigger,
    PromptInputSelectValue,
    PromptInputSubmit,
    PromptInputTextarea,
    PromptInputFooter,
    PromptInputTools,
} from '@/components/ai-elements/prompt-input';
import { useState } from 'react';
import { useChat } from '@ai-sdk/react';
import { GlobeIcon } from 'lucide-react';
import { Source, Sources, SourcesContent, SourcesTrigger } from '@/components/ai-elements/sources';
import { Loader } from '@/components/ai-elements/loader';
import { MessageParts } from '@/components/chat/MessageParts';

const models = [
    {
        name: 'GPT 4o',
        value: 'openai/gpt-4o',
    },
    {
        name: 'GPT 5',
        value: 'openai-gpt-5',
    },
];

const ChatBotDemo = () => {
    const [input, setInput] = useState('');
    const [model, setModel] = useState<string>(models[0].value);
    const [webSearch, setWebSearch] = useState(false);
    const { messages, sendMessage, status, regenerate } = useChat();

    const handleSubmit = (message: PromptInputMessage) => {
        const hasText = Boolean(message.text);
        const hasAttachments = Boolean(message.files?.length);

        if (!(hasText || hasAttachments)) {
            return;
        }

        sendMessage(
            {
                text: message.text || 'Sent with attachments',
                files: message.files,
            },
            {
                body: {
                    model: model,
                    webSearch: webSearch,
                },
            }
        );
        setInput('');
    };

    return (
        <div className="max-w-4xl mx-auto p-6 relative size-full h-screen">
            <div className="flex flex-col h-full">
                <Conversation className="h-full">
                    <ConversationContent>
                        {messages.map((message, index) => {
                            const isLastMessage = index === messages.length - 1;
                            return (
                                <div key={message.id}>
                                    {message.role === 'assistant' &&
                                        message.parts &&
                                        message.parts.filter((part) => part.type === 'source-url').length > 0 && (
                                            <Sources>
                                                <SourcesTrigger
                                                    count={message.parts.filter((part) => part.type === 'source-url').length}
                                                />
                                                {message.parts
                                                    .filter((part) => part.type === 'source-url')
                                                    .map((part, i) => (
                                                        <SourcesContent key={`${message.id}-${i}`}>
                                                            <Source
                                                                key={`${message.id}-${i}`}
                                                                href={part.url || ''}
                                                                title={part.url}
                                                            />
                                                        </SourcesContent>
                                                    ))}
                                            </Sources>
                                        )}
                                    {message.parts && (
                                        <MessageParts
                                            parts={message.parts}
                                            messageId={message.id}
                                            role={message.role}
                                            isLastMessage={isLastMessage}
                                            status={status}
                                            onRegenerate={regenerate}
                                        />
                                    )}
                                </div>
                            );
                        })}
                        {status === 'submitted' && <Loader />}
                    </ConversationContent>
                    <ConversationScrollButton />
                </Conversation>

                <PromptInput onSubmit={handleSubmit} className="mt-4" globalDrop multiple>
                    <PromptInputHeader>
                        <PromptInputAttachments>
                            {(attachment) => <PromptInputAttachment data={attachment} />}
                        </PromptInputAttachments>
                    </PromptInputHeader>
                    <PromptInputBody>
                        <PromptInputTextarea onChange={(e) => setInput(e.target.value)} value={input} />
                    </PromptInputBody>
                    <PromptInputFooter>
                        <PromptInputTools>
                            <PromptInputActionMenu>
                                <PromptInputActionMenuTrigger />
                                <PromptInputActionMenuContent>
                                    <PromptInputActionAddAttachments />
                                </PromptInputActionMenuContent>
                            </PromptInputActionMenu>
                            <PromptInputButton
                                variant={webSearch ? 'default' : 'ghost'}
                                onClick={() => setWebSearch(!webSearch)}
                            >
                                <GlobeIcon className="size-4" />
                                <span>Search</span>
                            </PromptInputButton>
                            <PromptInputSelect
                                onValueChange={(value) => {
                                    setModel(value);
                                }}
                                value={model}
                            >
                                <PromptInputSelectTrigger>
                                    <PromptInputSelectValue />
                                </PromptInputSelectTrigger>
                                <PromptInputSelectContent>
                                    {models.map((model) => (
                                        <PromptInputSelectItem key={model.value} value={model.value}>
                                            {model.name}
                                        </PromptInputSelectItem>
                                    ))}
                                </PromptInputSelectContent>
                            </PromptInputSelect>
                        </PromptInputTools>
                        <PromptInputSubmit disabled={!input && !status} status={status} />
                    </PromptInputFooter>
                </PromptInput>
            </div>
        </div>
    );
};

export default ChatBotDemo;
