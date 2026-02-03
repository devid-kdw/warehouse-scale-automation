import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Alert,
    Modal, TextInput, Checkbox, Badge, ActionIcon, Menu, Tabs, Stack, LoadingOverlay
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconSearch, IconDotsVertical, IconPlus, IconArchive, IconRestore, IconTrash, IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';
import { getArticles, createArticle, archiveArticle, restoreArticle, extractErrorMessage, deleteArticle } from '../api/services';
import { Article } from '../api/types';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';

export default function Articles() {
    const queryClient = useQueryClient();
    const [opened, { open, close }] = useDisclosure(false);
    const [filter, setFilter] = useState('');
    const [activeTab, setActiveTab] = useState<string | null>('active');

    // Fetch Articles based on tab
    const apiFilter = activeTab === 'active' ? 'true' : (activeTab === 'archived' ? 'false' : 'all');
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['articles', apiFilter],
        queryFn: () => getArticles(apiFilter as any),
    });

    const form = useForm({
        initialValues: {
            article_no: '',
            description: '',
            is_paint: false,
            is_active: true,
        },
        validate: {
            article_no: (val) => val.trim().length < 1 ? 'Article Number is required' : null,
            description: (val) => val.trim().length < 1 ? 'Description is required' : null,
        },
    });

    const handleSuccess = (message: string) => {
        notifications.show({
            title: 'Success',
            message,
            color: 'green',
            icon: <IconCheck size={16} />,
        });
        queryClient.invalidateQueries({ queryKey: ['articles'] });
    };

    const handleError = (err: unknown, action: string) => {
        notifications.show({
            title: 'Error',
            message: `${action} failed: ${extractErrorMessage(err)}`,
            color: 'red',
            icon: <IconX size={16} />,
        });
    };

    // Create Mutation
    const createMutation = useMutation({
        mutationFn: createArticle,
        onSuccess: () => {
            handleSuccess('Article created successfully');
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
        onSuccess: (_, variables) => {
            const verb = variables.action.charAt(0).toUpperCase() + variables.action.slice(1) + 'd'; // Archived, Restored, Deleted
            handleSuccess(`Article ${verb} successfully`);
        },
        onError: (err, variables) => {
            handleError(err, variables.action);
        }
    });

    const handleAction = (id: number, action: 'archive' | 'restore' | 'delete') => {
        const confirmMsg = action === 'delete'
            ? 'Are you sure you want to PERMANENTLY delete this article? This action cannot be undone.'
            : `Are you sure you want to ${action} this article?`;

        if (confirm(confirmMsg)) {
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
                {article.is_paint ? <Badge color="blue" variant="light">Paint</Badge> : <Badge color="gray" variant="light">Consumable</Badge>}
            </Table.Td>
            <Table.Td>
                {article.is_active
                    ? <Badge color="green" variant="dot">Active</Badge>
                    : <Badge color="yellow" variant="dot">Archived</Badge>
                }
            </Table.Td>
            <Table.Td>
                <Menu shadow="md" width={200}>
                    <Menu.Target>
                        <ActionIcon variant="subtle" color="gray"><IconDotsVertical size={16} /></ActionIcon>
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
                        <Menu.Divider />
                        <Menu.Item color="red" leftSection={<IconTrash size={14} />} onClick={() => handleAction(article.id, 'delete')}>
                            Delete
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

            {isError && (
                <Alert icon={<IconAlertCircle size={16} />} title="Error loading articles" color="red" mb="md">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <Group mb="md">
                    <TextInput
                        placeholder="Search by number or description..."
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

                {isLoading ? (
                    <LoadingState message="Loading articles..." />
                ) : filteredItems.length === 0 ? (
                    <EmptyState message="No articles found" />
                ) : (
                    <Table striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Article No.</Table.Th>
                                <Table.Th>Description</Table.Th>
                                <Table.Th>Type</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th style={{ width: 50 }}></Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <Modal opened={opened} onClose={close} title="Create New Article" centered>
                <form onSubmit={form.onSubmit((values) => createMutation.mutate(values as any))}>
                    <Stack>
                        <LoadingOverlay visible={createMutation.isPending} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />

                        {createMutation.isError && (
                            <Alert color="red" icon={<IconAlertCircle size={16} />}>
                                {extractErrorMessage(createMutation.error)}
                            </Alert>
                        )}

                        <TextInput
                            label="Article Number"
                            placeholder="e.g. 100-200"
                            withAsterisk
                            {...form.getInputProps('article_no')}
                        />

                        <TextInput
                            label="Description"
                            placeholder="Article name"
                            withAsterisk
                            {...form.getInputProps('description')}
                        />

                        <Checkbox
                            label="Is Paint?"
                            description="Check if this article is a paint product"
                            mt="xs"
                            {...form.getInputProps('is_paint', { type: 'checkbox' })}
                        />

                        <Checkbox
                            label="Active"
                            description="Uncheck to create as archived"
                            mt="xs"
                            {...form.getInputProps('is_active', { type: 'checkbox' })}
                        />

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
