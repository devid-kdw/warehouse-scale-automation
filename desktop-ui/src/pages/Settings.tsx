import { useState, useEffect } from 'react';
import { TextInput, Button, Paper, Title, Container, Group, Text, Alert } from '@mantine/core';
import { IconCheck, IconX, IconDatabase } from '@tabler/icons-react';
import { apiClient } from '../api/client';
import { checkHealth, extractErrorMessage } from '../api/services';
import { getBaseUrl, setBaseUrl } from '../api/auth';
import { useMutation } from '@tanstack/react-query';

export default function Settings() {
    const [baseUrlState, setBaseUrlState] = useState('');

    // Load initial values
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

            // 1. Check basic connectivity
            const health = await checkHealth();

            // 2. Verify we're authenticated (a protected endpoint would fail without valid JWT)
            try {
                await apiClient.get('/api/articles?limit=1');
            } catch (error) {
                const msg = extractErrorMessage(error);
                throw new Error(`Authentication failed: ${msg}`);
            }

            return health;
        }
    });

    return (
        <Container size="sm" py="xl">
            <Paper shadow="xs" p="xl" withBorder>
                <Title order={2} mb="md">Connection Settings</Title>

                <Text c="dimmed" size="sm" mb="lg">
                    Configure the connection to the Warehouse Backend API.
                </Text>

                <TextInput
                    label="API Base URL"
                    description="The URL where the backend is running (e.g. http://localhost:5001)"
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
                        Save & Test Connection
                    </Button>
                </Group>

                {testConnectionMutation.isSuccess && (
                    <Alert icon={<IconCheck size={16} />} title="Connected" color="green" mt="md">
                        Successfully connected to <strong>{testConnectionMutation.data.environment}</strong> environment.
                        <br />
                        DB Status: {testConnectionMutation.data.database}
                    </Alert>
                )}

                {testConnectionMutation.isError && (
                    <Alert icon={<IconX size={16} />} title="Connection Failed" color="red" mt="md">
                        {testConnectionMutation.error instanceof Error ? testConnectionMutation.error.message : 'Unknown error'}
                        <br />
                        Please check if the backend is running and you are logged in.
                    </Alert>
                )}

            </Paper>
        </Container>
    );
}
