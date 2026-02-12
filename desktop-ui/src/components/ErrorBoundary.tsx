import { Component, ReactNode } from 'react';
import { Container, Title, Text, Button, Stack, Paper } from '@mantine/core';
import { IconAlertTriangle } from '@tabler/icons-react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error?: Error; }

export class ErrorBoundary extends Component<Props, State> {
    state: State = { hasError: false };

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    render() {
        if (this.state.hasError) {
            return (
                <Container size="sm" py="xl">
                    <Paper shadow="sm" p="xl" withBorder>
                        <Stack align="center">
                            <IconAlertTriangle size={48} color="red" />
                            <Title order={3}>Something went wrong</Title>
                            <Text c="dimmed">{this.state.error?.message}</Text>
                            <Button onClick={() => window.location.reload()}>
                                Reload Application
                            </Button>
                        </Stack>
                    </Paper>
                </Container>
            );
        }
        return this.props.children;
    }
}
