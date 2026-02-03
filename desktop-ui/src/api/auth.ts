/**
 * Authentication store using sessionStorage (per prompt requirements).
 * 
 * Stores:
 * - access_token in sessionStorage
 * - refresh_token in sessionStorage  
 * - user info in memory
 */

export interface AuthUser {
    id: number;
    username: string;
    role: 'ADMIN' | 'OPERATOR';
    is_active: boolean;
}

export interface AuthState {
    isAuthenticated: boolean;
    user: AuthUser | null;
    accessToken: string | null;
    refreshToken: string | null;
}

// Storage keys (sessionStorage - tokens cleared when browser closes)
const STORAGE_KEYS = {
    ACCESS_TOKEN: 'auth_access_token',
    REFRESH_TOKEN: 'auth_refresh_token',
    USER: 'auth_user',
    BASE_URL: 'app_base_url',
};

// Initialize state from storage
function loadInitialState(): AuthState {
    const accessToken = sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const refreshToken = sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    const userStr = sessionStorage.getItem(STORAGE_KEYS.USER);

    let user: AuthUser | null = null;
    if (userStr) {
        try {
            user = JSON.parse(userStr);
        } catch {
            user = null;
        }
    }

    return {
        isAuthenticated: !!accessToken && !!user,
        user,
        accessToken,
        refreshToken,
    };
}

// Current state (in-memory, synced with sessionStorage)
let state: AuthState = loadInitialState();

// Listeners for state changes
type AuthListener = (state: AuthState) => void;
const listeners: Set<AuthListener> = new Set();

function notify() {
    listeners.forEach(listener => listener(state));
}

// --- Public API ---

export function getAuthState(): AuthState {
    return state;
}

export function subscribe(listener: AuthListener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
}

export function setTokens(accessToken: string, refreshToken: string, user: AuthUser) {
    sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    sessionStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    sessionStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));

    state = {
        isAuthenticated: true,
        user,
        accessToken,
        refreshToken,
    };
    notify();
}

export function updateAccessToken(accessToken: string) {
    sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    state = { ...state, accessToken };
    notify();
}

export function logout() {
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER);

    state = {
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
    };
    notify();
}

export function getAccessToken(): string | null {
    // Always read from sessionStorage for reliability in axios interceptors
    return sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
}

export function getRefreshToken(): string | null {
    // Always read from sessionStorage for reliability in axios interceptors
    return sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
}

export function getUser(): AuthUser | null {
    return state.user;
}

export function isAdmin(): boolean {
    return state.user?.role === 'ADMIN';
}

export function isAuthenticated(): boolean {
    return state.isAuthenticated;
}

// Base URL storage (persists across sessions)
export function getBaseUrl(): string {
    return localStorage.getItem(STORAGE_KEYS.BASE_URL) || 'http://localhost:5001';
}

export function setBaseUrl(url: string) {
    localStorage.setItem(STORAGE_KEYS.BASE_URL, url.replace(/\/$/, ''));
}
