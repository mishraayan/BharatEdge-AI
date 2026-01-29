import { useState } from 'react';
import { Download, CheckCircle, Loader2 } from 'lucide-react';

export default function SetupWizard({ onComplete }: { onComplete: () => void }) {
    const [step, setStep] = useState<'intro' | 'downloading' | 'complete'>('intro');
    const [progress, setProgress] = useState(0);
    const [statusText, setStatusText] = useState('Idle');

    const startDownload = async () => {
        setStep('downloading');
        setStatusText('Starting download of AI models (approx 2.5GB)...');

        // In a real implementation, we would call a backend endpoint that streams download progress.
        // For now, we'll simulate it to demonstrate the UI flow.
        let p = 0;
        const interval = setInterval(() => {
            p += Math.random() * 5;
            if (p >= 100) {
                p = 100;
                clearInterval(interval);
                setStatusText('Download complete! Optimizing for your CPU...');
                setTimeout(() => {
                    setStep('complete');
                }, 1500);
            }
            setProgress(p);
            if (p < 30) setStatusText(`Fetching LLM Brain... ${Math.round(p)}%`);
            else if (p < 70) setStatusText(`Downloading English & Bengali Dictionary... ${Math.round(p)}%`);
            else if (p < 95) setStatusText(`Finalizing RAG indexing tools... ${Math.round(p)}%`);
        }, 800);
    };

    return (
        <div className="h-screen w-full flex items-center justify-center bg-slate-900 text-white p-6 overflow-hidden">
            <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl overflow-hidden relative">
                {/* Background Glow */}
                <div className="absolute -top-24 -left-24 w-48 h-48 bg-indigo-600/20 blur-3xl rounded-full" />
                <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-purple-600/20 blur-3xl rounded-full" />

                <div className="relative z-10">
                    <div className="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/30 mx-auto">
                        <Download className="w-8 h-8 text-white" />
                    </div>

                    {step === 'intro' && (
                        <div className="text-center">
                            <h1 className="text-2xl font-bold mb-3">Welcome to BharatEdge AI</h1>
                            <p className="text-slate-400 mb-8 text-sm leading-relaxed">
                                To run 100% offline, we need to download the "AI Brain" (approx 2.5GB). You only need to do this once.
                            </p>
                            <button
                                onClick={startDownload}
                                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 transition-colors rounded-xl font-semibold flex items-center justify-center gap-2"
                            >
                                <Download className="w-5 h-5" /> Download & Setup
                            </button>
                            <p className="mt-4 text-[10px] text-slate-500">
                                This will download the Qwen2.5 3B model (GGUF) and Embedding models.
                            </p>
                        </div>
                    )}

                    {step === 'downloading' && (
                        <div className="text-center">
                            <h2 className="text-xl font-bold mb-4">Setting up your AI...</h2>
                            <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden mb-4">
                                <div
                                    className="h-full bg-indigo-500 transition-all duration-300 ease-out shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <p className="text-sm text-slate-300 mb-2 font-mono">{statusText}</p>
                            <div className="flex items-center justify-center gap-2 text-xs text-slate-500 animate-pulse">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                <span>Please do not close the app</span>
                            </div>
                        </div>
                    )}

                    {step === 'complete' && (
                        <div className="text-center animate-in fade-in zoom-in duration-500">
                            <div className="w-16 h-16 bg-green-500/20 border border-green-500/50 rounded-full flex items-center justify-center mb-6 mx-auto">
                                <CheckCircle className="w-8 h-8 text-green-500" />
                            </div>
                            <h2 className="text-2xl font-bold mb-2">Ready to Go!</h2>
                            <p className="text-slate-400 mb-8 text-sm">
                                BharatEdge AI is now fully operational and offline.
                            </p>
                            <button
                                onClick={onComplete}
                                className="w-full py-3 bg-green-600 hover:bg-green-500 transition-colors rounded-xl font-semibold shadow-lg shadow-green-900/20"
                            >
                                Start Chatting 🚀
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
