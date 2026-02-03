import { Container, Paper, Title, Text, List, ThemeIcon, Button, Group, Alert } from '@mantine/core';
import { IconCheck, IconServer, IconArrowRight, IconInfoCircle } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

export default function Inventory() {
    const navigate = useNavigate();

    return (
        <Container size="md" py="xl">
            <Group mb="lg">
                <ThemeIcon size={40} radius="md" color="blue" variant="light">
                    <IconServer size={24} />
                </ThemeIcon>
                <Title order={2}>Inventory</Title>
            </Group>

            <Alert icon={<IconInfoCircle size={16} />} title="Inventory Endpoint Missing" color="blue" mb="xl">
                The backend currently does not provide an endpoint to list stock or surplus levels (e.g., <code>GET /api/inventory</code>).
                However, the system tracks inventory adjustments centrally.
            </Alert>

            <Paper shadow="xs" p="xl" withBorder>
                <Title order={3} mb="md">What you can do now</Title>
                <Text mb="md">
                    While the inventory list view is under development, you can perform all other critical warehouse operations:
                </Text>

                <List
                    spacing="md"
                    size="sm"
                    center
                    icon={
                        <ThemeIcon color="teal" size={24} radius="xl">
                            <IconCheck size={16} />
                        </ThemeIcon>
                    }
                >
                    <List.Item>
                        <Group justify="space-between">
                            <Text>Create and Manage Articles</Text>
                            <Button variant="subtle" size="xs" onClick={() => navigate('/articles')} rightSection={<IconArrowRight size={14} />}>Go to Articles</Button>
                        </Group>
                    </List.Item>
                    <List.Item>
                        <Group justify="space-between">
                            <Text>Register new Batches</Text>
                            <Button variant="subtle" size="xs" onClick={() => navigate('/batches')} rightSection={<IconArrowRight size={14} />}>Go to Batches</Button>
                        </Group>
                    </List.Item>
                    <List.Item>
                        <Group justify="space-between">
                            <Text>Record Weigh-Ins (Drafts)</Text>
                            <Button variant="subtle" size="xs" onClick={() => navigate('/drafts/new')} rightSection={<IconArrowRight size={14} />}>New Draft</Button>
                        </Group>
                    </List.Item>
                    <List.Item>
                        <Group justify="space-between">
                            <Text>Approve or Reject Pending Drafts</Text>
                            <Button variant="subtle" size="xs" onClick={() => navigate('/drafts')} rightSection={<IconArrowRight size={14} />}>Go to Approvals</Button>
                        </Group>
                    </List.Item>
                </List>
            </Paper>

            <Paper shadow="xs" p="xl" withBorder mt="xl" bg="gray.1">
                <Title order={4} mb="xs">Note for Developers</Title>
                <Text size="sm" c="dimmed">
                    To enable the Inventory View, the backend must expose a <code>GET /api/inventory</code> endpoint returning aggregated stock and surplus by Article/Batch/Location.
                    Currently, inventory data resides in the <code>Stock</code> and <code>Surplus</code> tables but is only accessed via transaction logic.
                </Text>
            </Paper>
        </Container>
    );
}
