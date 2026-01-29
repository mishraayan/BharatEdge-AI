import { useHealth } from './hooks/useHealth';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import SetupWizard from './components/SetupWizard';
import { Loader2, AlertTriangle, RefreshCcw } from 'lucide-react';

function App() {
  const status = useHealth();

  if (status === 'loading') {
    return (
      <div className="h-screen w-full flex flex-col items-center justify-center bg-slate-50">
        <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
        <h2 className="text-lg font-semibold text-slate-700">Starting AI Engine...</h2>
        <p className="text-sm text-slate-500 mt-2">Loading models into RAM (Please wait)</p>
      </div>
    );
  }

  if (status === 'setup') {
    return <SetupWizard onComplete={() => window.location.reload()} />;
  }

  if (status === 'error') {
    return (
      <div className="h-screen w-full flex flex-col items-center justify-center bg-red-50">
        <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-lg font-bold text-red-700">Backend Connection Failed</h2>
        <p className="text-sm text-red-600 mt-2 max-w-md text-center">
          The Python AI server is not reachable. Please restart the application or check console logs.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 flex items-center gap-2"
        >
          <RefreshCcw className="w-4 h-4" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <ChatArea />
    </div>
  );
}

export default App;
