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
                // Keep status as loading or error if it takes too long
                if (status !== 'ready') setStatus('error');
            }
        };

        // Initial check
        checkHealth();

        // Poll every 2 seconds
        intervalId = setInterval(checkHealth, 2000);

        return () => clearInterval(intervalId);
    }, []);

    return status;
}
