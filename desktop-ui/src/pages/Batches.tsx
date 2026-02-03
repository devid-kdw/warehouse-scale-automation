import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text, Alert,
    Modal, TextInput, Select, Stack, LoadingOverlay, Badge
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconPlus, IconBox, IconAlertCircle, IconCheck, IconX } from '@tabler/icons-react';
import { Article, Batch } from '../api/types';
import { getArticles, getBatchesByArticle, createBatch, extractErrorMessage } from '../api/services';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';

export default function Batches() {
    const queryClient = useQueryClient();
    const [opened, { open, close }] = useDisclosure(false);
    const [selectedArticleNo, setSelectedArticleNo] = useState<string | null>(null);

    // Fetch Articles for dropdown
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'],
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map((a: Article) => ({
            value: a.article_no,
            label: `${a.article_no} - ${a.description}`,
            id: a.id // Need ID for create
        })),
    });

    // Fetch Batches for selected article
    const batchesQuery = useQuery({
        queryKey: ['batches', selectedArticleNo],
        queryFn: () => getBatchesByArticle(selectedArticleNo!),
        enabled: !!selectedArticleNo,
    });

    const createMutation = useMutation({
        mutationFn: createBatch,
        onSuccess: (data) => {
            notifications.show({
                title: 'Success',
                message: `Created batch ${data.batch_code} for article ${selectedArticleNo}`,
                color: 'green',
                icon: <IconCheck size={16} />,
            });
            queryClient.invalidateQueries({ queryKey: ['batches', selectedArticleNo] });
            close();
            form.reset();
        },
        onError: (err) => {
            notifications.show({
                title: 'Error',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
            });
        }
    });

    const form = useForm({
        initialValues: {
            batch_code: '',
        },
        validate: {
            batch_code: (val) => {
                const trimmed = val.trim();
                if (!/^\d+$/.test(trimmed)) return 'Digits only';
                const len = trimmed.length;
                if (!((len >= 4 && len <= 5) || (len >= 9 && len <= 12))) {
                    return 'Must be 4-5 or 9-12 digits';
                }
                return null;
            },
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        // Find article ID
        const article = articlesQuery.data?.find((a: any) => a.value === selectedArticleNo);
        if (!article) return;

        createMutation.mutate({
            article_id: article.id,
            batch_code: values.batch_code.trim()
        });
    };

    const rows = batchesQuery.data?.items.map((batch: Batch) => (
        <Table.Tr key={batch.id}>
            <Table.Td>{batch.id}</Table.Td>
            <Table.Td fw={700}>{batch.batch_code}</Table.Td>
            <Table.Td>
                {batch.is_active ? <Badge color="green" variant="dot">Active</Badge> : <Badge color="gray">Inactive</Badge>}
            </Table.Td>
            <Table.Td>{new Date(batch.created_at).toLocaleDateString()}</Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="lg" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Batches</Title>
                <Button
                    leftSection={<IconPlus size={16} />}
                    onClick={open}
                    disabled={!selectedArticleNo}
                >
                    New Batch
                </Button>
            </Group>

            <Paper shadow="xs" p="md" withBorder mb="lg">
                <Select
                    label="Select Article to view batches"
                    placeholder="Search article..."
                    data={articlesQuery.data || []}
                    searchable
                    value={selectedArticleNo}
                    onChange={setSelectedArticleNo}
                    leftSection={<IconBox size={16} />}
                />
            </Paper>

            <Paper shadow="xs" p="md" withBorder pos="relative" minH={200}>
                <LoadingOverlay visible={batchesQuery.isLoading && !!selectedArticleNo} overlayProps={{ radius: "sm", blur: 2 }} />

                {!selectedArticleNo ? (
                    <EmptyState message="Please select an article to view batches" />
                ) : batchesQuery.isError ? (
                    <Alert color="red" title="Error" icon={<IconAlertCircle size={16} />}>
                        {extractErrorMessage(batchesQuery.error)}
                    </Alert>
                ) : batchesQuery.data?.items.length === 0 ? (
                    <EmptyState message="No batches found for this article" />
                ) : (
                    <Table striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Batch Code</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>Created</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <Modal opened={opened} onClose={close} title={`New Batch for ${selectedArticleNo}`} centered>
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <Stack>
                        <LoadingOverlay visible={createMutation.isPending} zIndex={1000} />

                        <TextInput
                            label="Batch Code"
                            placeholder="Numeric code"
                            description="4-5 digits (Mankiewicz) or 9-12 digits (Akzo)"
                            withAsterisk
                            {...form.getInputProps('batch_code')}
                        />

                        {createMutation.isError && (
                            <Alert icon={<IconAlertCircle size={16} />} color="red">
                                {extractErrorMessage(createMutation.error)}
                            </Alert>
                        )}

                        <Group justify="flex-end" mt="md">
                            <Button variant="default" onClick={close}>Cancel</Button>
                            <Button type="submit" loading={createMutation.isPending}>Create Batch</Button>
                        </Group>
                    </Stack>
                </form>
            </Modal>
        </Container>
    );
}
