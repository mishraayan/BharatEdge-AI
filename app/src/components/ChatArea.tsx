import { useRef, useEffect, useState } from 'react';
import { Send, User, Bot, FileText, Square, X, AtSign } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useChat } from '../hooks/useChat';
import { endpoints } from '../api/client';
import clsx from 'clsx';

export default function ChatArea() {
    const { messages, sendMessage, isStreaming } = useChat();
    const [input, setInput] = useState('');
    const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
    const [availableDocs, setAvailableDocs] = useState<{ filename: string }[]>([]);
    const [showMentions, setShowMentions] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    const fetchDocs = async () => {
        try {
            const res = await fetch(endpoints.documents);
            const data = await res.json();
            setAvailableDocs(data);
        } catch (e) {
            console.error("Failed to fetch docs", e);
        }
    };

    useEffect(() => {
        fetchDocs();
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setInput(val);

        // Show mentions if there is an @ in the input
        if (val.includes('@')) {
            setShowMentions(true);
            fetchDocs(); // Refetch whenever user is typing with @ to ensure list is fresh
        } else {
            setShowMentions(false);
        }
    };

    const addDoc = (filename: string) => {
        if (!selectedDocs.includes(filename)) {
            setSelectedDocs([...selectedDocs, filename]);
        }
        // Remove the @ from input
        setInput(input.replace(/@$/, ''));
        setShowMentions(false);
    };

    const removeDoc = (filename: string) => {
        setSelectedDocs(selectedDocs.filter(d => d !== filename));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isStreaming) return;
        sendMessage(input, selectedDocs.length > 0 ? selectedDocs : undefined);
        setInput('');
        setSelectedDocs([]); // Clear filters after sending
    };

    return (
        <div className="flex-1 flex flex-col h-screen bg-white dark:bg-slate-950 transition-colors">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-300 dark:text-slate-600">
                        <Bot className="w-16 h-16 mb-4 opacity-50" />
                        <p className="text-lg font-medium text-slate-400 dark:text-slate-500">BharatEdge AI</p>
                        <p className="text-sm">Ask questions from your documents.</p>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={clsx("flex gap-4 max-w-4xl mx-auto", msg.role === 'user' ? "flex-row-reverse" : "")}>
                        <div className={clsx(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm",
                            msg.role === 'user' ? "bg-indigo-600 text-white" : "bg-emerald-600 text-white"
                        )}>
                            {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                        </div>

                        <div className={clsx(
                            "flex-1 p-4 rounded-lg text-sm leading-relaxed shadow-sm transition-colors",
                            msg.role === 'user'
                                ? "bg-indigo-50 dark:bg-indigo-900/30 text-slate-800 dark:text-slate-100"
                                : "bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-800"
                        )}>
                            {msg.role === 'assistant' ? (
                                <div className="prose prose-sm max-w-none prose-slate dark:prose-invert">
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                            ) : (
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                            )}

                            {/* Citations */}
                            {msg.citations && msg.citations.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700 flex flex-wrap gap-2">
                                    {msg.citations.map((cite, cIdx) => (
                                        <div key={cIdx} className="flex items-center gap-1.5 px-2 py-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded text-xs text-slate-500 dark:text-slate-400 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-300 cursor-pointer transition" title={cite.text}>
                                            <FileText className="w-3 h-3" />
                                            <span className="font-medium truncate max-w-[150px]">{cite.source}</span>
                                            <span className="text-slate-300">|</span>
                                            <span>p.{cite.page}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Performance Meta */}
                            {msg.meta && (
                                <div className="mt-2 flex items-center gap-2 text-[10px] text-slate-400 dark:text-slate-500 font-mono italic">
                                    <span>{msg.meta.tps} tokens/sec</span>
                                    <span>•</span>
                                    <span>{msg.meta.duration}s</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isStreaming && (
                    <div className="flex justify-center">
                        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce mx-1"></span>
                        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce mx-1 delay-100"></span>
                        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce mx-1 delay-200"></span>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 relative">
                <div className="max-w-4xl mx-auto relative">
                    {/* Mention List */}
                    {showMentions && (
                        <div className="absolute bottom-full left-0 mb-4 w-80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-indigo-500/50 dark:border-indigo-400/50 rounded-2xl shadow-[0_20px_50px_rgba(79,70,229,0.2)] overflow-hidden z-[9999] transition-all duration-300 ease-out animate-in fade-in slide-in-from-bottom-4 zoom-in-95">
                            <div className="p-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-[11px] font-bold uppercase tracking-[0.2em] flex justify-between items-center shadow-lg">
                                <div className="flex items-center gap-2">
                                    <AtSign className="w-3 h-3" />
                                    <span>Select Document</span>
                                </div>
                                <button onClick={() => setShowMentions(false)} className="hover:rotate-90 transition-transform duration-300"><X className="w-4 h-4" /></button>
                            </div>
                            <div className="max-h-72 overflow-y-auto p-2 space-y-1 custom-scrollbar">
                                {availableDocs.length === 0 ? (
                                    <div className="p-6 text-xs text-center text-slate-500 italic flex flex-col items-center gap-2">
                                        <Bot className="w-8 h-8 opacity-20" />
                                        <span>No documents found in backend.<br />Try uploading some PDFs first!</span>
                                    </div>
                                ) : (
                                    availableDocs.map((doc) => (
                                        <button
                                            key={doc.filename}
                                            onClick={() => addDoc(doc.filename)}
                                            className="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-indigo-500/10 dark:hover:bg-indigo-400/10 hover:translate-x-1 rounded-lg flex items-center gap-3 group transition-all duration-200 border-b border-slate-100/50 dark:border-slate-800/50 last:border-0"
                                        >
                                            <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-md group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900/50 transition-colors">
                                                <FileText className="w-4 h-4 text-slate-500 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
                                            </div>
                                            <span className="truncate font-medium group-hover:text-indigo-600 dark:group-hover:text-indigo-400">{doc.filename}</span>
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    )}

                    {/* Selected Chips */}
                    {selectedDocs.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                            {selectedDocs.map(doc => (
                                <div key={doc} className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-indigo-50 to-indigo-100/50 dark:from-indigo-950/40 dark:to-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-full text-xs text-indigo-700 dark:text-indigo-300 animate-in zoom-in-90 duration-300 shadow-sm hover:scale-105 transition-transform cursor-default">
                                    <AtSign className="w-3 h-3 text-indigo-500" />
                                    <span className="font-semibold max-w-[200px] truncate">{doc}</span>
                                    <button
                                        onClick={() => removeDoc(doc)}
                                        className="p-1 hover:bg-indigo-200 dark:hover:bg-indigo-800 rounded-full transition-colors ml-1"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                </div>
                            ))}
                            <button
                                onClick={() => setSelectedDocs([])}
                                className="text-[10px] text-slate-400 hover:text-red-500 underline transition-colors"
                            >
                                Clear all
                            </button>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={handleInputChange}
                            placeholder={selectedDocs.length > 0 ? "Ask about selected documents..." : "Ask a question (type @ to filter docs)..."}
                            className="w-full pl-4 pr-12 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 shadow-sm transition text-slate-900 dark:text-white placeholder:text-slate-400"
                            disabled={isStreaming}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isStreaming}
                            className="absolute right-2 top-2 p-1.5 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                        >
                            {isStreaming ? <Square className="w-5 h-5 fill-current" /> : <Send className="w-5 h-5" />}
                        </button>
                    </form>
                </div>
                <div className="text-center mt-2 text-xs text-slate-400 dark:text-slate-600">
                    Answers generated locally. Check citations for accuracy.
                </div>
            </div>
        </div>
    );
}
