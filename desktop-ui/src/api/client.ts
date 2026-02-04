import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ApiErrorResponse } from './types';
import {
    getAccessToken,
    getRefreshToken,
    updateAccessToken,
    logout,
    getBaseUrl
} from './auth';
import { notifications } from '@mantine/notifications';

// Default configuration
const DEFAULT_BASE_URL = 'http://localhost:5001';

// Create Axios instance
export const apiClient = axios.create({
    baseURL: DEFAULT_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else if (token) {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Request interceptor: inject JWT token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    // Update base URL from storage
    const storedUrl = getBaseUrl();
    if (storedUrl) {
        // In DEV, use proxy for localhost
        if (import.meta.env.DEV && (storedUrl.includes('localhost') || storedUrl.includes('127.0.0.1'))) {
            config.baseURL = '';
        } else {
            config.baseURL = storedUrl;
        }
    } else if (import.meta.env.DEV) {
        config.baseURL = '';
    }

    // Skip auth for public endpoints
    const isPublicEndpoint = config.url?.includes('/health') || config.url?.includes('/auth/login');

    // Inject access token
    const token = getAccessToken();
    console.log('[API Client] Request to:', config.url, 'Token present:', !!token, 'isPublic:', isPublicEndpoint);

    if (token && !isPublicEndpoint) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('[API Client] Added Authorization header');
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

// Response interceptor: handle 401, refresh token
apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiErrorResponse>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // If 401 and not already retrying
        if (error.response?.status === 401 && !originalRequest._retry) {
            // Don't retry login or refresh endpoints
            if (originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')) {
                return Promise.reject(error);
            }

            if (isRefreshing) {
                // Queue this request until refresh completes
                return new Promise((resolve, reject) => {
                    failedQueue.push({
                        resolve: (token: string) => {
                            originalRequest.headers.Authorization = `Bearer ${token}`;
                            resolve(apiClient(originalRequest));
                        },
                        reject
                    });
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const refreshToken = getRefreshToken();
            if (!refreshToken) {
                // No refresh token, logout
                logout();
                notifications.show({
                    title: 'Session Expired',
                    message: 'Please login again.',
                    color: 'red',
                });
                window.location.hash = '#/login';
                return Promise.reject(error);
            }

            try {
                // Attempt to refresh
                const response = await axios.post(
                    `${getBaseUrl()}/api/auth/refresh`,
                    {},
                    { headers: { Authorization: `Bearer ${refreshToken}` } }
                );

                const newAccessToken = response.data.access_token;
                updateAccessToken(newAccessToken);

                // Process queued requests
                processQueue(null, newAccessToken);

                // Retry original request
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return apiClient(originalRequest);

            } catch (refreshError) {
                // Refresh failed, logout
                processQueue(refreshError as Error, null);
                logout();
                notifications.show({
                    title: 'Session Expired',
                    message: 'Please login again.',
                    color: 'red',
                });
                window.location.hash = '#/login';
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        // Handle 403 Forbidden
        if (error.response?.status === 403) {
            notifications.show({
                title: 'Insufficient Permissions',
                message: 'You do not have permission to perform this action.',
                color: 'red',
            });
        }

        return Promise.reject(error);
    }
);

// Legacy storage keys (removed, now using auth.ts)
// Storage keys
export const STORAGE_KEYS = {
    BASE_URL: 'app_base_url',
    API_TOKEN: 'app_api_token',
    ACTOR_ID: 'app_actor_id',
};
