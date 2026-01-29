import { useState, useEffect } from 'react';
import { endpoints } from '../api/client';

export type BackendStatus = 'loading' | 'ready' | 'error' | 'setup';

export function useHealth() {
    const [status, setStatus] = useState<BackendStatus>('loading');

    useEffect(() => {
        let intervalId: any;

        const checkHealth = async () => {
            try {
                const res = await fetch(endpoints.health);
                if (res.ok) {
                    const data = await res.json();
                    if (data.model_exists === false) {
                        setStatus('setup');
                    } else if (data.llm_loaded === true || data.status === 'ok') {
                        setStatus('ready');
                        clearInterval(intervalId);
                    }
                }
            } catch (err) {
                console.error("Health check failed", err);
                // Keep status as loading during the first few seconds of startup
                // Only set error if it persists
            }
        };

        // ...

        // Set a timeout to declare absolute failure only after 30 seconds
        const timeoutId = setTimeout(() => {
            setStatus(s => s === 'ready' || s === 'setup' ? s : 'error');
        }, 30000); // Give it plenty of time for 8GB RAM users

        // Initial check
        checkHealth();

        // Poll every 2 seconds
        intervalId = setInterval(checkHealth, 2000);

        return () => {
            clearInterval(intervalId);
            clearTimeout(timeoutId);
        };
    }, []);

    return status;
}
