import { useState, useEffect } from 'react';
import { getAuthState, subscribe, AuthState } from '../api/auth';

export function useAuth() {
    const [authState, setAuthState] = useState<AuthState>(getAuthState());

    useEffect(() => {
        return subscribe(setAuthState);
    }, []);

    return authState;
}
