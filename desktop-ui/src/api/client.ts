import axios, { AxiosError } from 'axios';
import { ApiErrorResponse } from './types';

// Constants for LocalStorage keys
export const STORAGE_KEYS = {
    BASE_URL: 'app_base_url',
    API_TOKEN: 'app_api_token',
    ACTOR_ID: 'app_actor_id',
};

// Default configuration
const DEFAULT_BASE_URL = 'http://localhost:5001';

// Create Axios instance
export const apiClient = axios.create({
    baseURL: DEFAULT_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Inject Token and dynamic Base URL
apiClient.interceptors.request.use((config) => {
    const storedUrl = localStorage.getItem(STORAGE_KEYS.BASE_URL);
    const token = localStorage.getItem(STORAGE_KEYS.API_TOKEN);

    // Update Base URL if stored, but respect proxy in DEV
    if (storedUrl && config.baseURL !== storedUrl) {
        // In DEV, if the user has localhost:5001 or 127.0.0.1:5001 configured, 
        // ignore it and use relative path to hit the proxy
        if (import.meta.env.DEV && (storedUrl.includes('localhost') || storedUrl.includes('127.0.0.1'))) {
            config.baseURL = '';
        } else {
            config.baseURL = storedUrl;
        }
    } else if (import.meta.env.DEV && config.baseURL === DEFAULT_BASE_URL) {
        config.baseURL = ''; // Default to relative in dev
    }

    // Inject Token (skip for public endpoints)
    const isPublicEndpoint = config.url?.endsWith('/health');
    if (token && !isPublicEndpoint) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

// Response Interceptor: Standardize Errors
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiErrorResponse>) => {
        // If we have a standardized backend error, we can try to format it? 
        // Or just pass it through. 
        // For now, allow components to handle specific error codes.

        // Global 401 handling could go here, but UI might want to show a banner instead of redirecting silently.
        // We will let the query wrapper handling this.
        return Promise.reject(error);
    }
);
