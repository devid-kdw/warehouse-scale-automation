import { useState, useEffect } from 'react';
import { TextInput, Button, Paper, Title, Container, Group, Text, Alert } from '@mantine/core';
import { IconCheck, IconX, IconDatabase } from '@tabler/icons-react';
import { STORAGE_KEYS, apiClient } from '../api/client';
import { checkHealth, extractErrorMessage } from '../api/services';
import { useMutation } from '@tanstack/react-query';

export default function Settings() {
    const [baseUrl, setBaseUrl] = useState('');
    const [token, setToken] = useState('');
    const [actorId, setActorId] = useState('');

    // Load initial values
    useEffect(() => {
        setBaseUrl(localStorage.getItem(STORAGE_KEYS.BASE_URL) || 'http://localhost:5001');
        setToken(localStorage.getItem(STORAGE_KEYS.API_TOKEN) || '');
        setActorId(localStorage.getItem(STORAGE_KEYS.ACTOR_ID) || '1');
    }, []);

    const saveSettings = () => {
        const cleanBaseUrl = baseUrl.trim().replace(/\/$/, '') || 'http://localhost:5001'; // Default if empty
        const cleanToken = token.trim().replace(/^Bearer\s+/i, ''); // Remove "Bearer " prefix if present

        localStorage.setItem(STORAGE_KEYS.BASE_URL, cleanBaseUrl);
        localStorage.setItem(STORAGE_KEYS.API_TOKEN, cleanToken);
        localStorage.setItem(STORAGE_KEYS.ACTOR_ID, actorId);
    };

    const testConnectionMutation = useMutation({
        mutationFn: async () => {
            saveSettings(); // Save so client picks up new token

            // 1. Check basic connectivity
            const health = await checkHealth();

            // 2. Verify Token (call a protected endpoint)
            // We use getArticles with a small limit if possible, or just the list
            try {
                // If this fails with 401, the mutation will fail
                await apiClient.get('/api/articles?limit=1');
            } catch (error) {
                const msg = extractErrorMessage(error);
                throw new Error(`Token verification failed: ${msg}`);
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
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    mb="md"
                    required
                />

                <TextInput
                    label="API Token"
                    description="Bearer token for authentication"
                    placeholder="Enter your API token"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    mb="md"
                    type="password"
                />

                <TextInput
                    label="Actor User ID"
                    description="ID of the user performing actions (Default: 1)"
                    placeholder="1"
                    value={actorId}
                    onChange={(e) => setActorId(e.target.value)}
                    mb="xl"
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
                        Successfully connected into <strong>{testConnectionMutation.data.environment}</strong> environment.
                        <br />
                        DB Status: {testConnectionMutation.data.database}
                    </Alert>
                )}

                {testConnectionMutation.isError && (
                    <Alert icon={<IconX size={16} />} title="Connection Failed" color="red" mt="md">
                        {testConnectionMutation.error instanceof Error ? testConnectionMutation.error.message : 'Unknown error'}
                        <br />
                        Please check if the backend is running and the URL is correct.
                    </Alert>
                )}

            </Paper>
        </Container>
    );
}
