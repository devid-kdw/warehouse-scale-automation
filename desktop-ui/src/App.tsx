import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell, Group, Text, Button, Menu } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconLogout, IconUser } from '@tabler/icons-react';
import { Sidebar } from './components/Sidebar';
import Settings from './pages/Settings';
import Login from './pages/Login';
import DraftEntry from './pages/Drafts/DraftEntry';
import DraftApproval from './pages/Drafts/DraftApproval';
import Articles from './pages/Articles';
import Batches from './pages/Batches';
import Inventory from './pages/Inventory';
import Reports from './pages/Reports';
import Receiving from './pages/Receiving';
import ReceiptHistory from './pages/Inventory/ReceiptHistory';
import logo from './assets/enikon-logo.jpg';
import BulkDraftEntry from './pages/Drafts/BulkDraftEntry';
import { logout } from './api/auth';
import { ErrorBoundary } from './components/ErrorBoundary';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        }
    }
});

import { useAuth } from './hooks/useAuth';
function RequireAuth({ children }: { children: React.ReactNode }) {
    const auth = useAuth();
    const location = useLocation();

    if (!auth.isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}

// Admin-only route wrapper
function RequireAdmin({ children }: { children: React.ReactNode }) {
    const auth = useAuth();

    if (!auth.isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (auth.user?.role !== 'ADMIN') {
        notifications.show({
            title: 'Access Denied',
            message: 'You do not have permission to view this page.',
            color: 'red',
        });
        return <Navigate to="/drafts/new" replace />;
    }

    return <>{children}</>;
}

function Layout() {
    const auth = useAuth();

    const handleLogout = () => {
        logout();
        window.location.hash = '#/login';
    };

    return (
        <AppShell
            header={{ height: 60 }}
            navbar={{ width: 250, breakpoint: 'sm' }}
            padding="md"
        >
            <AppShell.Header>
                <Group h="100%" px="md" justify="space-between">
                    <Group>
                        <img src={logo} alt="Enikon Aerospace" style={{ height: 40 }} />
                        <Text c="white" fw={700} size="lg">Warehouse Ops</Text>
                    </Group>

                    {auth.isAuthenticated && auth.user && (
                        <Menu shadow="md" width={200}>
                            <Menu.Target>
                                <Button
                                    variant="subtle"
                                    color="gray"
                                    leftSection={<IconUser size={16} />}
                                >
                                    {auth.user.username} ({auth.user.role})
                                </Button>
                            </Menu.Target>
                            <Menu.Dropdown>
                                <Menu.Item
                                    leftSection={<IconLogout size={14} />}
                                    onClick={handleLogout}
                                    color="red"
                                >
                                    Logout
                                </Menu.Item>
                            </Menu.Dropdown>
                        </Menu>
                    )}
                </Group>
            </AppShell.Header>

            <AppShell.Navbar p="xs">
                <Sidebar isAdmin={auth.user?.role === 'ADMIN'} />
            </AppShell.Navbar>

            <AppShell.Main>
                <Routes>
                    {/* Operator + Admin */}
                    <Route path="/drafts/new" element={
                        <RequireAuth><DraftEntry /></RequireAuth>
                    } />

                    {/* Admin only */}
                    <Route path="/drafts" element={
                        <RequireAdmin><DraftApproval /></RequireAdmin>
                    } />
                    <Route path="/drafts/bulk" element={
                        <RequireAdmin><BulkDraftEntry /></RequireAdmin>
                    } />
                    <Route path="/articles" element={
                        <RequireAdmin><Articles /></RequireAdmin>
                    } />
                    <Route path="/batches" element={
                        <RequireAdmin><Batches /></RequireAdmin>
                    } />
                    <Route path="/inventory" element={
                        <RequireAdmin><Inventory /></RequireAdmin>
                    } />
                    <Route path="/receiving" element={
                        <RequireAdmin><Receiving /></RequireAdmin>
                    } />
                    <Route path="/inventory/receipts" element={
                        <RequireAdmin><ReceiptHistory /></RequireAdmin>
                    } />
                    <Route path="/reports" element={
                        <RequireAdmin><Reports /></RequireAdmin>
                    } />

                    {/* Settings - both */}
                    <Route path="/settings" element={
                        <RequireAuth><Settings /></RequireAuth>
                    } />

                    {/* Default redirect */}
                    <Route path="*" element={
                        auth.isAuthenticated
                            ? <Navigate to={auth.user?.role === 'ADMIN' ? '/drafts' : '/drafts/new'} replace />
                            : <Navigate to="/login" replace />
                    } />
                </Routes>
            </AppShell.Main>
        </AppShell>
    );
}

function App() {
    return (
        <ErrorBoundary>
            <QueryClientProvider client={queryClient}>
                <HashRouter>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/*" element={<Layout />} />
                    </Routes>
                </HashRouter>
            </QueryClientProvider>
        </ErrorBoundary>
    );
}

export default App;
