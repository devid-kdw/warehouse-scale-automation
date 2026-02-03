import { useState, useEffect } from 'react';
import { STORAGE_KEYS } from '../api/client';

interface AppSettings {
    baseUrl: string;
    apiToken: string;
    actorId: string;
}

export function useAppSettings() {
    const [settings, setSettings] = useState<AppSettings>({
        baseUrl: '',
        apiToken: '',
        actorId: '',
    });

    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        const baseUrl = localStorage.getItem(STORAGE_KEYS.BASE_URL) || 'http://localhost:5001';
        const apiToken = localStorage.getItem(STORAGE_KEYS.API_TOKEN) || '';
        const actorId = localStorage.getItem(STORAGE_KEYS.ACTOR_ID) || '1';

        setSettings({ baseUrl, apiToken, actorId });
        setIsLoaded(true);
    }, []);

    const saveSettings = (newSettings: AppSettings) => {
        localStorage.setItem(STORAGE_KEYS.BASE_URL, newSettings.baseUrl);
        localStorage.setItem(STORAGE_KEYS.API_TOKEN, newSettings.apiToken);
        localStorage.setItem(STORAGE_KEYS.ACTOR_ID, newSettings.actorId);
        setSettings(newSettings);

        // Force reload of axios config if needed, or trigger a re-render context
        // For now, simpler to just assume the client.ts reads from localStorage on request
        // or we might need to reload the page to ensure axios picks it up if it was a singleton
        // But client.ts seems to read on interceptor, so it should be fine.
    };

    return {
        settings,
        saveSettings,
        isLoaded
    };
}
