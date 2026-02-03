import { Navigate, useLocation } from 'react-router-dom';
import { getAuthState } from '../api/auth';

interface RequireRoleProps {
    children: JSX.Element;
    allowedRoles: string[];
}

export const RequireRole = ({ children, allowedRoles }: RequireRoleProps) => {
    const auth = getAuthState();
    const location = useLocation();

    if (!auth.isAuthenticated || !auth.user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (!allowedRoles.includes(auth.user.role)) {
        // If Operator tries to access Admin page, redirect to default Operator page
        if (auth.user.role === 'OPERATOR') {
            return <Navigate to="/drafts/new" replace />;
        }
        // Fallback for others
        return <Navigate to="/" replace />;
    }

    return children;
};
