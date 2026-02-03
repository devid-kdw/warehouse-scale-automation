import { NavLink as RouterNavLink, useLocation } from 'react-router-dom';
import { NavLink, Box, Stack, Text, ThemeIcon, Group } from '@mantine/core';
import {
    IconSettings, IconScale, IconChecklist, IconPackage,
    IconTags, IconServer, IconPlugConnected, IconPlugX, IconFileSpreadsheet, IconPackageImport
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { checkHealth } from '../api/services';

interface SidebarProps {
    isAdmin?: boolean;
}

export function Sidebar({ isAdmin = false }: SidebarProps) {
    const location = useLocation();

    // Polling health check for connectivity banner
    const { data: health, isError } = useQuery({
        queryKey: ['health'],
        queryFn: checkHealth,
        refetchInterval: 10000,
        retry: false
    });

    const isConnected = !isError && !!health;

    // Define links with role requirements
    const allLinks = [
        { icon: IconScale, label: 'Draft Entry', to: '/drafts/new', roles: ['ADMIN', 'OPERATOR'] },
        { icon: IconChecklist, label: 'Draft Approvals', to: '/drafts', roles: ['ADMIN'] },
        { icon: IconPackage, label: 'Articles', to: '/articles', roles: ['ADMIN'] },
        { icon: IconTags, label: 'Batches', to: '/batches', roles: ['ADMIN'] },
        { icon: IconPackageImport, label: 'Receiving', to: '/receiving', roles: ['ADMIN'] },
        { icon: IconServer, label: 'Inventory', to: '/inventory', roles: ['ADMIN'] },
        { icon: IconFileSpreadsheet, label: 'Reports', to: '/reports', roles: ['ADMIN'] },
        { icon: IconSettings, label: 'Settings', to: '/settings', roles: ['ADMIN', 'OPERATOR'] },
    ];

    // Filter links based on role
    const links = allLinks.filter(link =>
        isAdmin || link.roles.includes('OPERATOR')
    );

    return (
        <Stack h="100%" gap={0} justify="space-between">
            <Box p="md" style={{ borderBottom: '1px solid var(--mantine-color-gray-3)' }}>
                <Group mt="xs" gap="xs">
                    <ThemeIcon color={isConnected ? 'green' : 'red'} variant="light" size="sm">
                        {isConnected ? <IconPlugConnected size={12} /> : <IconPlugX size={12} />}
                    </ThemeIcon>
                    <Text size="xs" c={isConnected ? 'green' : 'red'} fw={500}>
                        {isConnected ? 'Online' : 'Disconnected'}
                    </Text>
                </Group>
            </Box>

            <Box flex={1} py="md">
                {links.map((item) => (
                    <NavLink
                        key={item.label}
                        component={RouterNavLink}
                        to={item.to}
                        label={item.label}
                        leftSection={<item.icon size={16} stroke={1.5} />}
                        active={location.pathname === item.to || location.pathname.startsWith(item.to + '/')}
                        variant="light"
                        disabled={!isConnected && item.to !== '/settings'}
                    />
                ))}
            </Box>

            {!isConnected && (
                <Box p="md" bg="red.1">
                    <Text size="xs" c="red.9">
                        Connection lost. Please check Settings.
                    </Text>
                </Box>
            )}
        </Stack>
    );
}
