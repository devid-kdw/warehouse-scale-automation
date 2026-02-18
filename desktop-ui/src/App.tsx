import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell, Group, Text, Button, Menu } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconLogout, IconUser } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { Sidebar } from './components/Sidebar';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import Settings from './pages/Settings';
import Login from './pages/Login';
import DraftEntry from './pages/Drafts/DraftEntry';
import DraftApproval from './pages/Drafts/DraftApproval';
// import Articles from './pages/Articles'; // Decommissioned
import Inventory from './pages/Inventory';
import Reports from './pages/Reports';
import Receiving from './pages/Receiving';
import { IdentifikatorLookup } from './pages/Identifikator/Lookup';
import { IdentifikatorAdminQueue } from './pages/Identifikator/AdminQueue';
import OpenOrders from './pages/Orders/OpenOrders';
import ClosedOrders from './pages/Orders/ClosedOrders';
import OrderDetail from './pages/Orders/OrderDetail';
import CreateOrder from './pages/Orders/CreateOrder';
import logo from './assets/enikon-logo.jpg';
import Izlaz from './pages/Entries/Izlaz';
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
    const { t } = useTranslation('common');

    if (!auth.isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (auth.user?.role !== 'ADMIN') {
        notifications.show({
            title: t('auth.accessDenied'),
            message: t('auth.noPermission'),
            color: 'red',
        });
        return <Navigate to="/drafts/new" replace />;
    }

    return <>{children}</>;
}

function Layout() {
    const auth = useAuth();
    const { t } = useTranslation('common');

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
                        <Text c="white" fw={700} size="lg">{t('app.title')}</Text>
                    </Group>

                    {auth.isAuthenticated && auth.user && (
                        <Group gap="xs">
                            <LanguageSwitcher />
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
                                        {t('user.logout')}
                                    </Menu.Item>
                                </Menu.Dropdown>
                            </Menu>
                        </Group>
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
                    <Route path="/izlaz" element={
                        <RequireAdmin><Izlaz /></RequireAdmin>
                    } />

                    {/* Orders Module */}
                    <Route path="/orders/open" element={
                        <RequireAdmin><OpenOrders /></RequireAdmin>
                    } />
                    <Route path="/orders/closed" element={
                        <RequireAdmin><ClosedOrders /></RequireAdmin>
                    } />
                    <Route path="/orders/new" element={
                        <RequireAdmin><CreateOrder /></RequireAdmin>
                    } />
                    <Route path="/orders/:id" element={
                        <RequireAdmin><OrderDetail /></RequireAdmin>
                    } />

                    {/* Articles route removed */}

                    <Route path="/inventory" element={
                        <RequireAuth><Inventory /></RequireAuth>
                    } />
                    <Route path="/receiving" element={
                        <RequireAdmin><Receiving /></RequireAdmin>
                    } />

                    <Route path="/reports" element={
                        <RequireAdmin><Reports /></RequireAdmin>
                    } />

                    {/* Identifikator */}
                    <Route path="/identifikator" element={
                        <RequireAuth><IdentifikatorLookup /></RequireAuth>
                    } />
                    <Route path="/identifikator/queue" element={
                        <RequireAdmin><IdentifikatorAdminQueue /></RequireAdmin>
                    } />

                    {/* Settings - ADMIN only (T18/T19 RBAC fix) */}
                    <Route path="/settings" element={
                        <RequireAdmin><Settings /></RequireAdmin>
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
