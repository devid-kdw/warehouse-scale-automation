import { useState, useEffect } from 'react';
import { TextInput, Button, Paper, Title, Container, Group, Text, Alert } from '@mantine/core';
import { IconCheck, IconX, IconDatabase } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../api/client';
import { checkHealth, extractErrorMessage } from '../api/services';
import { getBaseUrl, setBaseUrl } from '../api/auth';
import { useMutation } from '@tanstack/react-query';

export default function Settings() {
    const { t } = useTranslation('common');
    const [baseUrlState, setBaseUrlState] = useState('');

    useEffect(() => {
        setBaseUrlState(getBaseUrl());
    }, []);

    const saveSettings = () => {
        const cleanBaseUrl = baseUrlState.trim().replace(/\/$/, '') || 'http://localhost:5001';
        setBaseUrl(cleanBaseUrl);
    };

    const testConnectionMutation = useMutation({
        mutationFn: async () => {
            saveSettings();

            const health = await checkHealth();

            try {
                await apiClient.get('/api/articles?limit=1');
            } catch (error) {
                const msg = extractErrorMessage(error);
                throw new Error(`Autentifikacija nije uspjela: ${msg}`);
            }

            return health;
        }
    });

    return (
        <Container size="sm" py="xl">
            <Paper shadow="xs" p="xl" withBorder>
                <Title order={2} mb="md">{t('settings.title')}</Title>

                <Text c="dimmed" size="sm" mb="lg">
                    {t('settings.description')}
                </Text>

                <TextInput
                    label={t('settings.apiBaseUrl')}
                    description={t('settings.apiBaseUrlDesc')}
                    placeholder="http://localhost:5001"
                    value={baseUrlState}
                    onChange={(e) => setBaseUrlState(e.target.value)}
                    mb="xl"
                    required
                />

                <Group justify="flex-end">
                    <Button
                        leftSection={<IconDatabase size={16} />}
                        loading={testConnectionMutation.isPending}
                        onClick={() => testConnectionMutation.mutate()}
                    >
                        {t('settings.saveAndTest')}
                    </Button>
                </Group>

                {testConnectionMutation.isSuccess && (
                    <Alert icon={<IconCheck size={16} />} title={t('settings.connected')} color="green" mt="md">
                        {t('settings.connectedMsg')} <strong>{testConnectionMutation.data.environment}</strong>.
                        <br />
                        {t('settings.dbStatus')}: {testConnectionMutation.data.database}
                    </Alert>
                )}

                {testConnectionMutation.isError && (
                    <Alert icon={<IconX size={16} />} title={t('settings.connectionFailed')} color="red" mt="md">
                        {testConnectionMutation.error instanceof Error ? testConnectionMutation.error.message : 'Nepoznata greška'}
                        <br />
                        {t('settings.checkBackend')}
                    </Alert>
                )}

            </Paper>
        </Container>
    );
}
