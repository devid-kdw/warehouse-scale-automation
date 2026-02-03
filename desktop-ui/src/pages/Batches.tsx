import { useState } from 'react';
import {
    Container, Title, Paper, Group, Button, Select, TextInput,
    Text, Box, Table, Badge, LoadingOverlay
} from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconPlus, IconCheck, IconX } from '@tabler/icons-react';
import { getArticles, getBatchesByArticle, createBatch, extractErrorMessage } from '../api/services';
import { EmptyState } from '../components/common/EmptyState';
import dayjs from 'dayjs';

export default function Batches() {
    const queryClient = useQueryClient();
    const [selectedArticleNo, setSelectedArticleNo] = useState<string | null>(null);

    const form = useForm({
        initialValues: {
            article_id: '',
            batch_code: '',
            expiry_date: null as Date | null,
        },
        validate: {
            article_id: (value) => !value ? 'Article is required' : null,
            batch_code: (value) => {
                if (!value) return 'Batch code is required';
                // Strict validation: 4 digits OR 9-12 digits
                if (!/^\d{4}$|^\d{9,12}$/.test(value)) {
                    return 'Code must be 4 digits (Mankiewicz) or 9-12 digits (Akzo)';
                }
                return null;
            },
            expiry_date: (value) => !value ? 'Expiry date is required' : null, // Optional in backend but mandatory in UI per spec
        },
    });

    // Fetch active articles for dropdown
    const articlesQuery = useQuery({
        queryKey: ['articles', 'active'],
        queryFn: () => getArticles('true'),
    });

    // Fetch batches when article is selected
    const batchesQuery = useQuery({
        queryKey: ['batches', selectedArticleNo],
        queryFn: () => getBatchesByArticle(selectedArticleNo!),
        enabled: !!selectedArticleNo,
    });

    const createMutation = useMutation({
        mutationFn: createBatch,
        onSuccess: () => {
            notifications.show({
                title: 'Success',
                message: 'Batch created successfully',
                color: 'green',
                icon: <IconCheck size="1.1rem" />,
            });
            form.reset();
            // Preserve selected article
            if (selectedArticleNo) {
                const article = articlesQuery.data?.items.find(a => a.article_no === selectedArticleNo);
                if (article) form.setFieldValue('article_id', article.id.toString());
            }
            queryClient.invalidateQueries({ queryKey: ['batches', selectedArticleNo] });
        },
        onError: (error) => {
            notifications.show({
                title: 'Error',
                message: extractErrorMessage(error),
                color: 'red',
                icon: <IconX size="1.1rem" />,
            });
        },
    });

    const handleSubmit = form.onSubmit((values) => {
        createMutation.mutate({
            article_id: parseInt(values.article_id),
            batch_code: values.batch_code,
            expiry_date: values.expiry_date ? dayjs(values.expiry_date).format('YYYY-MM-DD') : undefined
        });
    });

    // Handle Article Change
    const handleArticleChange = (value: string | null) => {
        form.setFieldValue('article_id', value || '');
        if (value) {
            const article = articlesQuery.data?.items.find(a => a.id.toString() === value);
            setSelectedArticleNo(article?.article_no || null);
        } else {
            setSelectedArticleNo(null);
        }
    };

    const isSubmitting = createMutation.isPending;

    return (
        <Container size="xl">
            <Title order={2} mb="xl">Batch Management</Title>

            <Group align="flex-start" gap="xl">
                {/* Create Form */}
                <Paper shadow="xs" p="md" withBorder style={{ width: 350, flexShrink: 0 }}>
                    <Title order={4} mb="md">New Batch</Title>
                    <form onSubmit={handleSubmit}>
                        <Select
                            label="Article"
                            placeholder="Select article"
                            data={articlesQuery.data?.items.map(a => ({
                                value: a.id.toString(),
                                label: `${a.article_no} - ${a.description}`
                            })) || []}
                            searchable
                            mb="md"
                            {...form.getInputProps('article_id')}
                            onChange={handleArticleChange}
                            disabled={isSubmitting}
                        />

                        <TextInput
                            label="Batch Code"
                            placeholder="Scan or type code"
                            mb="md"
                            {...form.getInputProps('batch_code')}
                        />

                        <DatePickerInput
                            label="Expiry Date"
                            placeholder="Pick date"
                            valueFormat="DD.MM.YYYY"
                            mb="xl"
                            {...form.getInputProps('expiry_date')}
                        />

                        <Button
                            fullWidth
                            leftSection={<IconPlus size={16} />}
                            type="submit"
                            loading={isSubmitting}
                        >
                            Create Batch
                        </Button>
                    </form>
                </Paper>

                {/* Batches List */}
                <Paper shadow="xs" p="md" withBorder style={{ flex: 1 }} pos="relative" mih={400}>
                    <LoadingOverlay visible={batchesQuery.isLoading} />

                    {!selectedArticleNo ? (
                        <Box h={300} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Text c="dimmed" size="lg">Select an article to view batches</Text>
                        </Box>
                    ) : batchesQuery.data?.items.length === 0 ? (
                        <EmptyState message="No batches found for this article" />
                    ) : (
                        <Table striped highlightOnHover>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Batch Code</Table.Th>
                                    <Table.Th>Expiry Date</Table.Th>
                                    <Table.Th>Created</Table.Th>
                                    <Table.Th>Status</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {batchesQuery.data?.items.map((batch) => {
                                    const isExpired = batch.expiry_date && dayjs(batch.expiry_date).isBefore(dayjs());
                                    return (
                                        <Table.Tr key={batch.id}>
                                            <Table.Td fw={700}>{batch.batch_code}</Table.Td>
                                            <Table.Td>
                                                <Text c={isExpired ? 'red' : undefined} fw={isExpired ? 700 : 400}>
                                                    {batch.expiry_date ? dayjs(batch.expiry_date).format('DD.MM.YYYY') : '-'}
                                                </Text>
                                            </Table.Td>
                                            <Table.Td>{dayjs(batch.created_at).format('DD.MM.YYYY')}</Table.Td>
                                            <Table.Td>
                                                <Badge
                                                    color={batch.is_active ? 'green' : 'gray'}
                                                    variant={batch.is_active ? 'light' : 'outline'}
                                                >
                                                    {batch.is_active ? 'Active' : 'Archived'}
                                                </Badge>
                                            </Table.Td>
                                        </Table.Tr>
                                    );
                                })}
                            </Table.Tbody>
                        </Table>
                    )}
                </Paper>
            </Group>
        </Container>
    );
}
