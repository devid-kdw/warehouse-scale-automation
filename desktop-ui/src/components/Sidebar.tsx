import { NavLink as RouterNavLink, useLocation } from 'react-router-dom';
import { NavLink, Box, Stack, Text, ThemeIcon, Group } from '@mantine/core';
import {
    IconSettings, IconScale, IconChecklist,
    IconServer, IconPlugConnected, IconPlugX, IconFileSpreadsheet, IconPackageImport,
    IconTable, IconScan, IconUserQuestion
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { checkHealth } from '../api/services';

interface SidebarProps {
    isAdmin?: boolean;
}

export function Sidebar({ isAdmin = false }: SidebarProps) {
    const location = useLocation();
    const { t } = useTranslation('common');

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
        // OPERATOR & ADMIN
        { icon: IconScale, labelKey: 'nav.drafts', to: '/drafts/new', roles: ['ADMIN', 'OPERATOR'] },
        // P1 fix: izlaz is OPERATOR+ADMIN
        { icon: IconTable, labelKey: 'izlaz.title', to: '/izlaz', roles: ['ADMIN', 'OPERATOR'] },


        // ORDERS MODULE (ADMIN ONLY)
        {
            icon: IconPackageImport,
            labelKey: 'nav.orders',
            roles: ['ADMIN'],
            children: [
                { labelKey: 'nav.openOrders', to: '/orders/open' },
                { labelKey: 'nav.receiving', to: '/receiving' }, // Move receiving here
                { labelKey: 'nav.closedOrders', to: '/orders/closed' },
            ]
        },

        // ADMIN ONLY
        { icon: IconServer, labelKey: 'nav.inventory', to: '/inventory', roles: ['ADMIN', 'OPERATOR'] },
        // P1 fix: use i18n keys for identifikator nav
        { icon: IconScan, labelKey: 'nav.identifikator', to: '/identifikator', roles: ['ADMIN', 'OPERATOR'] },
        { icon: IconUserQuestion, labelKey: 'nav.missingItems', to: '/identifikator/queue', roles: ['ADMIN'] },
        { icon: IconChecklist, labelKey: 'nav.approvals', to: '/drafts', roles: ['ADMIN'] },
        // P1 fix: /articles removed from nav (legacy screen decommissioned per TASK-0030)
        { icon: IconFileSpreadsheet, labelKey: 'nav.reports', to: '/reports', roles: ['ADMIN'] },

        // ADMIN ONLY
        { icon: IconSettings, labelKey: 'nav.settings', to: '/settings', roles: ['ADMIN'] },
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
                        {isConnected ? 'Online' : t('app.disconnected')}
                    </Text>
                </Group>
            </Box>

            <Box flex={1} py="md">
                {links.map((item) => {
                    if (item.children) {
                        return (
                            <Box key={item.labelKey} mb="sm">
                                <Text size="xs" fw={700} c="dimmed" px="md" mb={4} style={{ textTransform: 'uppercase' }}>
                                    {t(item.labelKey)}
                                </Text>
                                {item.children.map(child => (
                                    <NavLink
                                        key={child.labelKey}
                                        component={RouterNavLink}
                                        to={child.to}
                                        label={t(child.labelKey)}
                                        leftSection={<Box w={16} />} // Indent
                                        active={location.pathname === child.to || location.pathname.startsWith(child.to + '/')}
                                        variant="light"
                                        disabled={!isConnected}
                                    />
                                ))}
                            </Box>
                        );
                    }
                    return (
                        <NavLink
                            key={item.labelKey}
                            component={RouterNavLink}
                            to={item.to}
                            label={t(item.labelKey)}
                            leftSection={item.icon ? <item.icon size={16} stroke={1.5} /> : null}
                            active={location.pathname === item.to || location.pathname.startsWith(item.to + '/')}
                            variant="light"
                            disabled={!isConnected && item.to !== '/settings'}
                        />
                    );
                })}
            </Box>

            {!isConnected && (
                <Box p="md" bg="red.1">
                    <Text size="xs" c="red.9">
                        {t('app.disconnected')}. {t('nav.settings')}.
                    </Text>
                </Box>
            )}
        </Stack>
    );
}
