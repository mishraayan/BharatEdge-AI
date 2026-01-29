import { useState, useRef, useCallback } from 'react';
import { endpoints } from '../api/client';

export interface Citation {
    source: string;
    page: number;
    text: string;
}

export interface Message {
    role: 'user' | 'assistant';
    content: string;
    citations?: Citation[];
    meta?: { tps: number; duration: number };
}

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(async (text: string, sources?: string[]) => {
        // 1. Add User Message
        const userMsg: Message = { role: 'user', content: text };
        setMessages((prev) => [...prev, userMsg]);
        setIsStreaming(true);

        // 2. Prepare for Assistant Message
        const assistantMsg: Message = { role: 'assistant', content: '', citations: [] };
        setMessages((prev) => [...prev, assistantMsg]);

        abortControllerRef.current = new AbortController();

        try {
            const response = await fetch(endpoints.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: text,
                    history: messages.map(m => ({ role: m.role, content: m.content })).slice(-5), // Send last 5 turns
                    sources: sources || null
                }),
                signal: abortControllerRef.current.signal,
            });

            if (!response.ok) throw new Error('Network error');
            if (!response.body) throw new Error('No body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');

                // Keep the last chunk if incomplete
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const event = JSON.parse(line);

                        setMessages((prev) => {
                            const newMsgs = [...prev];
                            const lastIdx = newMsgs.length - 1;
                            const lastMsg = { ...newMsgs[lastIdx] }; // IMMUTABLE COPY

                            if (event.type === 'token') {
                                lastMsg.content += event.data;
                            } else if (event.type === 'citation') {
                                lastMsg.citations = event.data;
                            } else if (event.type === 'meta') {
                                lastMsg.meta = { tps: event.tps, duration: event.duration };
                            } else if (event.type === 'done') {
                                setIsStreaming(false);
                            }

                            newMsgs[lastIdx] = lastMsg;
                            return newMsgs;
                        });

                    } catch (e) {
                        console.error("JSON Parse Error", e, line);
                    }
                }
            }

        } catch (err: any) {
            if (err.name !== 'AbortError') {
                setMessages((prev) => {
                    const newMsgs = [...prev];
                    const lastIdx = newMsgs.length - 1;
                    if (lastIdx >= 0 && newMsgs[lastIdx].role === 'assistant') {
                        newMsgs[lastIdx] = {
                            ...newMsgs[lastIdx],
                            content: 'Connection failed. The AI engine might be reloading or busy. Please retry.'
                        };
                    } else {
                        newMsgs.push({ role: 'assistant', content: 'Connection failed. Please retry.' });
                    }
                    return newMsgs;
                });
            }
        } finally {
            setIsStreaming(false);
        }
    }, [messages]);

    return { messages, sendMessage, isStreaming };
}
