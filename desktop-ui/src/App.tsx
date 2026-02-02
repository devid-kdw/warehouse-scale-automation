import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell, Group, Text } from '@mantine/core';
import { Sidebar } from './components/Sidebar';
import Settings from './pages/Settings';
import DraftEntry from './pages/Drafts/DraftEntry';
import DraftApproval from './pages/Drafts/DraftApproval';
import { Articles, Batches, Inventory } from './pages/Placeholders'; // Still placeholders for now

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        }
    }
});

function Layout() {
    return (
        <AppShell
            header={{ height: 60 }}
            navbar={{ width: 250, breakpoint: 'sm' }}
            padding="md"
        >
            <AppShell.Header>
                <Group h="100%" px="md" align="center">
                    <img src="./src/assets/enikon-logo.jpg" alt="Enikon Aerospace" style={{ height: 40 }} />
                    <Text c="white" fw={700} size="lg">Warehouse Ops</Text>
                </Group>
            </AppShell.Header>

            <AppShell.Navbar p="xs">
                <Sidebar />
            </AppShell.Navbar>

            <AppShell.Main>
                <Routes>
                    <Route path="/drafts/new" element={<DraftEntry />} />
                    <Route path="/drafts" element={<DraftApproval />} />
                    <Route path="/articles" element={<Articles />} />
                    <Route path="/batches" element={<Batches />} />
                    <Route path="/inventory" element={<Inventory />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="*" element={<Navigate to="/settings" replace />} />
                </Routes>
            </AppShell.Main>
        </AppShell>
    );
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <HashRouter>
                <Layout />
            </HashRouter>
        </QueryClientProvider>
    );
}

export default App;
