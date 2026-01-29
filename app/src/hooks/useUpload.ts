import { useState } from 'react';
import { endpoints } from '../api/client';

export function useUpload() {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const uploadFile = async (file: File) => {
        setIsUploading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch(endpoints.upload, {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) throw new Error('Upload failed');

            const data = await res.json();
            return data; // { filename, chunks_count, status }
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setIsUploading(false);
        }
    };

    return { uploadFile, isUploading, error };
}
