import { useState } from 'react';
import {
    Container, Paper, Title, Select, TextInput, NumberInput,
    Button, Group, Stack, Alert, ActionIcon, Tooltip
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useQuery, useMutation } from '@tanstack/react-query';
import { IconRefresh, IconCheck, IconX } from '@tabler/icons-react';
import { v4 as uuidv4 } from 'uuid';
import { getArticles, getBatchesByArticle, createDraft } from '../../api/services';
import { extractErrorMessage } from '../../api/services';
import { useNavigate } from 'react-router-dom';

export default function DraftEntry() {
    const navigate = useNavigate();
    const [successMsg, setSuccessMsg] = useState('');

    const form = useForm({
        initialValues: {
            location_id: '1',
            article_id: '',
            batch_id: '',
            quantity_kg: 0,
            client_event_id: uuidv4(),
        },
        validate: {
            location_id: (val) => !val ? 'Location ID is required' : null,
            article_id: (val) => !val ? 'Article is required' : null,
            batch_id: (val) => !val ? 'Batch is required' : null,
            quantity_kg: (val) => val <= 0 ? 'Quantity must be greater than 0' : null,
            client_event_id: (val) => !val ? 'Event ID is required' : null,
        },
    });

    // Regenerate UUID helper
    const regenerateUuid = () => form.setFieldValue('client_event_id', uuidv4());

    // Fetch Articles
    const articlesQuery = useQuery({
        queryKey: ['articles'],
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map(a => ({ value: a.id.toString(), label: `${a.article_no} - ${a.description}`, article_no: a.article_no })),
    });

    // Fetch Batches (dependent on Article)
    const selectedArticle = articlesQuery.data?.find(a => a.value === form.values.article_id);
    const batchesQuery = useQuery({
        queryKey: ['batches', selectedArticle?.article_no],
        queryFn: () => getBatchesByArticle(selectedArticle!.article_no),
        enabled: !!selectedArticle?.article_no,
        select: (data) => data.items.map(b => ({ value: b.id.toString(), label: b.batch_code })),
    });

    // Create Draft Mutation
    const mutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            // Convert string IDs to numbers where needed by API
            return createDraft({
                location_id: parseInt(values.location_id),
                article_id: parseInt(values.article_id),
                batch_id: parseInt(values.batch_id),
                quantity_kg: values.quantity_kg,
                client_event_id: values.client_event_id
            });
        },
        onSuccess: () => {
            setSuccessMsg(`Draft created successfully! (Event: ${form.values.client_event_id.slice(0, 8)}...)`);
            form.reset();
            form.setFieldValue('client_event_id', uuidv4()); // Gen new ID for next
            // Clear success after 5s
            setTimeout(() => setSuccessMsg(''), 5000);
        },
        onError: () => {
            setSuccessMsg('');
        }
    });

    return (
        <Container size="sm" py="xl">
            <Paper shadow="xs" p="xl" withBorder>
                <Title order={2} mb="lg">Manual Weigh-In Entry</Title>

                {successMsg && (
                    <Alert icon={<IconCheck size={16} />} title="Success" color="green" mb="md" withCloseButton onClose={() => setSuccessMsg('')}>
                        {successMsg}
                        <Button variant="subtle" size="xs" onClick={() => navigate('/drafts')}>View Dashboard</Button>
                    </Alert>
                )}

                {mutation.isError && (
                    <Alert icon={<IconX size={16} />} title="Error" color="red" mb="md">
                        {extractErrorMessage(mutation.error)}
                    </Alert>
                )}

                <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                    <Stack>
                        <TextInput
                            label="Location ID"
                            description="Default is 1 (Main Scale). Change only if needed."
                            {...form.getInputProps('location_id')}
                        />

                        <Select
                            label="Article"
                            placeholder="Select article"
                            data={articlesQuery.data || []}
                            searchable
                            nothingFoundMessage="No articles found"
                            disabled={articlesQuery.isLoading}
                            {...form.getInputProps('article_id')}
                            // Reset batch when article changes
                            onChange={(val) => {
                                form.setFieldValue('article_id', val || '');
                                form.setFieldValue('batch_id', '');
                            }}
                        />

                        <Select
                            label="Batch"
                            placeholder={!form.values.article_id ? "Select an article first" : "Select batch"}
                            data={batchesQuery.data || []}
                            searchable
                            disabled={!form.values.article_id || batchesQuery.isLoading}
                            {...form.getInputProps('batch_id')}
                        />

                        <NumberInput
                            label="Quantity (kg)"
                            placeholder="0.00"
                            decimalScale={2}
                            fixedDecimalScale
                            min={0.01}
                            step={0.1}
                            {...form.getInputProps('quantity_kg')}
                        />

                        <Group align="flex-end" gap="xs">
                            <TextInput
                                label="Client Event ID"
                                style={{ flex: 1 }}
                                readOnly
                                {...form.getInputProps('client_event_id')}
                            />
                            <Tooltip label="Generate new UUID">
                                <ActionIcon variant="light" size="lg" mb={2} onClick={regenerateUuid}>
                                    <IconRefresh size={18} />
                                </ActionIcon>
                            </Tooltip>
                        </Group>

                        <Button type="submit" loading={mutation.isPending} mt="md">
                            Submit Draft
                        </Button>
                    </Stack>
                </form>
            </Paper>
        </Container>
    );
}
