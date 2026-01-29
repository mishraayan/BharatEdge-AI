export const API_BASE = "http://localhost:8000";

export const endpoints = {
    health: `${API_BASE}/health`,
    chat: `${API_BASE}/chat`,
    upload: `${API_BASE}/documents/upload`,
    documents: `${API_BASE}/documents`,
};
