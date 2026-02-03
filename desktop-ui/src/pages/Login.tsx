import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container, Paper, Title, TextInput, PasswordInput, Button,
    Alert, Text, Stack, Box
} from '@mantine/core';
import { IconLock, IconUser, IconAlertCircle, IconDatabase } from '@tabler/icons-react';
import { apiClient } from '../api/client';
import { setTokens, setBaseUrl, getBaseUrl, AuthUser } from '../api/auth';
import logo from '../assets/enikon-logo.jpg';

interface LoginResponse {
    access_token: string;
    refresh_token: string;
    user: AuthUser;
}

export default function Login() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [baseUrl, setBaseUrlState] = useState(getBaseUrl());
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            // Save base URL before login attempt
            setBaseUrl(baseUrl);

            const response = await apiClient.post<LoginResponse>('/api/auth/login', {
                username,
                password,
            });

            const { access_token, refresh_token, user } = response.data;

            // Save tokens and user info
            setTokens(access_token, refresh_token, user);

            // Navigate based on role
            if (user.role === 'ADMIN') {
                navigate('/drafts');
            } else {
                navigate('/drafts/new');
            }

        } catch (err: any) {
            const message = err.response?.data?.error?.message
                || err.response?.data?.msg
                || err.message
                || 'Login failed';
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #1a1b1e 0%, #25262b 100%)'
            }}
        >
            <Container size="xs">
                <Paper shadow="xl" p="xl" radius="md" withBorder>
                    {/* Logo and Title */}
                    <Stack align="center" mb="xl">
                        <img src={logo} alt="Enikon Aerospace" style={{ height: 60 }} />
                        <Title order={2}>Warehouse Ops</Title>
                        <Text c="dimmed" size="sm">Sign in to continue</Text>
                    </Stack>

                    {/* Login Form */}
                    <form onSubmit={handleLogin}>
                        <Stack>
                            <TextInput
                                label="Username"
                                placeholder="Enter username"
                                leftSection={<IconUser size={16} />}
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                autoComplete="username"
                            />

                            <PasswordInput
                                label="Password"
                                placeholder="Enter password"
                                leftSection={<IconLock size={16} />}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete="current-password"
                            />

                            {/* Advanced Settings Toggle */}
                            <Button
                                variant="subtle"
                                size="xs"
                                onClick={() => setShowAdvanced(!showAdvanced)}
                                leftSection={<IconDatabase size={14} />}
                            >
                                {showAdvanced ? 'Hide' : 'Show'} Server Settings
                            </Button>

                            {showAdvanced && (
                                <TextInput
                                    label="Backend URL"
                                    description="URL of the warehouse backend server"
                                    placeholder="http://localhost:5001"
                                    value={baseUrl}
                                    onChange={(e) => setBaseUrlState(e.target.value)}
                                />
                            )}

                            {error && (
                                <Alert
                                    icon={<IconAlertCircle size={16} />}
                                    color="red"
                                    variant="light"
                                >
                                    {error}
                                </Alert>
                            )}

                            <Button
                                type="submit"
                                loading={loading}
                                fullWidth
                                size="md"
                                mt="md"
                            >
                                Sign In
                            </Button>
                        </Stack>
                    </form>

                    {/* Footer */}
                    <Text c="dimmed" size="xs" ta="center" mt="xl">
                        Default credentials: stefan / ChangeMe123!
                    </Text>
                </Paper>
            </Container>
        </Box>
    );
}
