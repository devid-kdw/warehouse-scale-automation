import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text, Alert,
    Modal, TextInput, Checkbox, Badge, ActionIcon, Menu, Tabs, Stack
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconSearch, IconDotsVertical, IconPlus, IconArchive, IconRestore, IconTrash } from '@tabler/icons-react';
import { getArticles, createArticle, archiveArticle, restoreArticle, extractErrorMessage, deleteArticle } from '../api/services';
import { Article } from '../api/types';

export default function Articles() {
    const queryClient = useQueryClient();
    const [opened, { open, close }] = useDisclosure(false);
    const [filter, setFilter] = useState('');
    const [activeTab, setActiveTab] = useState<string | null>('active');

    // Fetch Articles based on tab
    const apiFilter = activeTab === 'active' ? 'true' : (activeTab === 'archived' ? 'false' : 'all');
    const { data, isLoading } = useQuery({
        queryKey: ['articles', apiFilter],
        queryFn: () => getArticles(apiFilter as any),
    });

    // Create Mutation
    const createMutation = useMutation({
        mutationFn: createArticle,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['articles'] });
            close();
            form.reset();
        },
    });

    // Archive/Restore/Delete Mutations
    const actionMutation = useMutation({
        mutationFn: async ({ id, action }: { id: number, action: 'archive' | 'restore' | 'delete' }) => {
            if (action === 'archive') return archiveArticle(id);
            if (action === 'restore') return restoreArticle(id);
            if (action === 'delete') return deleteArticle(id);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['articles'] });
        }
    });

    const form = useForm({
        initialValues: {
            article_no: '',
            description: '',
            is_paint: true,
            is_active: true,
        },
        validate: {
            article_no: (val) => val.length < 1 ? 'Required' : null,
            description: (val) => val.length < 1 ? 'Required' : null,
        },
    });

    const handleAction = (id: number, action: 'archive' | 'restore' | 'delete') => {
        if (confirm(`Are you sure you want to ${action} this article?`)) {
            actionMutation.mutate({ id, action });
        }
    };

    const filteredItems = data?.items.filter((item: Article) =>
        item.article_no.toLowerCase().includes(filter.toLowerCase()) ||
        (item.description || '').toLowerCase().includes(filter.toLowerCase())
    ) || [];

    const rows = filteredItems.map((article: Article) => (
        <Table.Tr key={article.id} style={{ opacity: article.is_active ? 1 : 0.6 }}>
            <Table.Td>{article.article_no}</Table.Td>
            <Table.Td>{article.description}</Table.Td>
            <Table.Td>
                {article.is_paint ? <Badge color="blue">Paint</Badge> : <Badge color="gray">Consumable</Badge>}
            </Table.Td>
            <Table.Td>{article.is_active ? 'Active' : 'Archived'}</Table.Td>
            <Table.Td>
                <Menu shadow="md" width={200}>
                    <Menu.Target>
                        <ActionIcon variant="subtle"><IconDotsVertical size={16} /></ActionIcon>
                    </Menu.Target>
                    <Menu.Dropdown>
                        {article.is_active ? (
                            <Menu.Item leftSection={<IconArchive size={14} />} onClick={() => handleAction(article.id, 'archive')}>
                                Archive
                            </Menu.Item>
                        ) : (
                            <Menu.Item leftSection={<IconRestore size={14} />} onClick={() => handleAction(article.id, 'restore')}>
                                Restore
                            </Menu.Item>
                        )}
                        <Menu.Item color="red" leftSection={<IconTrash size={14} />} onClick={() => handleAction(article.id, 'delete')}>
                            Delete (Danger)
                        </Menu.Item>
                    </Menu.Dropdown>
                </Menu>
            </Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="lg" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Articles</Title>
                <Button leftSection={<IconPlus size={16} />} onClick={open}>New Article</Button>
            </Group>

            {actionMutation.isError && (
                <Alert title="Action Failed" color="red" mb="md" withCloseButton onClose={actionMutation.reset}>
                    {extractErrorMessage(actionMutation.error)}
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <Group mb="md">
                    <TextInput
                        placeholder="Search articles..."
                        leftSection={<IconSearch size={16} />}
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        style={{ flex: 1 }}
                    />
                </Group>

                <Tabs value={activeTab} onChange={setActiveTab} mb="md">
                    <Tabs.List>
                        <Tabs.Tab value="active">Active</Tabs.Tab>
                        <Tabs.Tab value="archived">Archived</Tabs.Tab>
                        <Tabs.Tab value="all">All</Tabs.Tab>
                    </Tabs.List>
                </Tabs>

                <Table>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>No.</Table.Th>
                            <Table.Th>Description</Table.Th>
                            <Table.Th>Type</Table.Th>
                            <Table.Th>Status</Table.Th>
                            <Table.Th>Action</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>{rows}</Table.Tbody>
                </Table>
                {filteredItems.length === 0 && !isLoading && <Text ta="center" py="xl" c="dimmed">No articles found</Text>}
            </Paper>

            <Modal opened={opened} onClose={close} title="Create New Article">
                <form onSubmit={form.onSubmit((values) => createMutation.mutate(values as any))}>
                    <Stack>
                        <TextInput label="Article Number" placeholder="e.g. 100-200" {...form.getInputProps('article_no')} required />
                        <TextInput label="Description" placeholder="Article name" {...form.getInputProps('description')} required />
                        <Checkbox label="Is Paint?" {...form.getInputProps('is_paint', { type: 'checkbox' })} />

                        {createMutation.isError && (
                            <Alert color="red">{extractErrorMessage(createMutation.error)}</Alert>
                        )}

                        <Group justify="flex-end" mt="md">
                            <Button variant="default" onClick={close}>Cancel</Button>
                            <Button type="submit" loading={createMutation.isPending}>Create</Button>
                        </Group>
                    </Stack>
                </form>
            </Modal>
        </Container>
    );
}
