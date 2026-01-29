
import { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, RefreshCw, Moon, Sun, Trash2 } from 'lucide-react';
import { useUpload } from '../hooks/useUpload';
import { useTheme } from '../hooks/useTheme';
import clsx from 'clsx';
// ...
// ...
export default function Sidebar() {
    const { uploadFile, isUploading, error } = useUpload();
    const { theme, toggleTheme } = useTheme();
    const [docs, setDocs] = useState<string[]>([]);

    const fetchDocs = async () => {
        try {
            const listRes = await fetch("http://localhost:8000/documents");
            if (listRes.ok) {
                const data = await listRes.json();
                setDocs(data.map((d: any) => d.filename));
            }
        } catch (e) {
            console.error("Failed to fetch docs", e);
        }
    };

    useEffect(() => {
        fetchDocs();
    }, []);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            try {
                await uploadFile(e.target.files[0]);
                fetchDocs(); // Refresh list
            } catch (e) {
                // Error handled in hook
            }
        }
    };

    return (
        <div className="w-64 bg-slate-100 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-screen flex flex-col p-4 transition-colors">
            <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-6 flex items-center gap-2">
                <span className="text-indigo-600 dark:text-indigo-400">🇮🇳</span> BharatEdge
            </h1>

            {/* Upload Section */}
            <div className="mb-6">
                <label className={clsx(
                    "flex items-center justify-center w-full h-24 px-4 transition border-2 border-dashed rounded-lg appearance-none cursor-pointer focus:outline-none",
                    "bg-white dark:bg-slate-800",
                    isUploading
                        ? "border-indigo-400 bg-indigo-50 dark:bg-slate-800"
                        : "border-slate-300 dark:border-slate-700 hover:border-indigo-600 dark:hover:border-indigo-500"
                )}>
                    <div className="flex flex-col items-center space-y-2">
                        {isUploading ? (
                            <Loader2 className="w-6 h-6 text-indigo-600 animate-spin" />
                        ) : (
                            <Upload className="w-6 h-6 text-slate-400 dark:text-slate-500" />
                        )}
                        <span className="font-medium text-slate-600 dark:text-slate-300 text-sm text-center">
                            {isUploading ? "Processing..." : "Drop PDF / Txt"}
                        </span>
                    </div>
                    <input type="file" className="hidden" onChange={handleFileChange} disabled={isUploading} accept=".pdf,.txt" />
                </label>
                {error && (
                    <div className="mt-2 text-xs text-red-500 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> {error}
                    </div>
                )}
            </div>

            {/* Document List */}
            <div className="flex-1 overflow-y-auto">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Documents</h2>
                    <button onClick={fetchDocs} className="text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400">
                        <RefreshCw className="w-3 h-3" />
                    </button>
                </div>

                {docs.length === 0 ? (
                    <p className="text-xs text-slate-400 italic">No documents indexed.</p>
                ) : (
                    <ul className="space-y-2">
                        {docs.map((doc, idx) => (
                            <li key={idx} className="group flex items-center gap-2 text-sm text-slate-700 dark:text-slate-200 p-2 bg-white dark:bg-slate-800 rounded shadow-sm border border-transparent dark:border-slate-700 hover:border-indigo-200 dark:hover:border-slate-600 transition">
                                <FileText className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                                <span className="truncate flex-1">{doc}</span>
                                <button
                                    onClick={async (e) => {
                                        e.stopPropagation();
                                        if (!confirm('Delete ' + doc + '?')) return;
                                        try {
                                            await fetch(`http://localhost:8000/documents/${doc}`, { method: 'DELETE' });
                                            fetchDocs();
                                        } catch (err) { console.error(err); }
                                    }}
                                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-500 transition"
                                    title="Delete File"
                                >
                                    <Trash2 className="w-3.5 h-3.5" />
                                </button>
                                <CheckCircle className="w-3 h-3 text-green-500" />
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Footer & Theme Toggle */}
            <div className="mt-auto pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="text-xs text-slate-400 dark:text-slate-500">
                    V1.4 Standard
                </div>
                <button
                    onClick={toggleTheme}
                    className="p-1.5 rounded-md text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-800 dark:text-slate-400 transition"
                    title="Toggle Theme"
                >
                    {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </button>
            </div>
        </div>
    );
}

