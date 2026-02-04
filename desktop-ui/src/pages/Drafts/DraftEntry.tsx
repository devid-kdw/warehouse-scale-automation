import { useEffect } from 'react';
import {
    Container, Paper, Title, Select, TextInput, NumberInput,
    Button, Group, Stack, Alert, ActionIcon, Tooltip, Text, Anchor
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconRefresh, IconCheck, IconX, IconAlertTriangle } from '@tabler/icons-react';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';
import { getArticles, getBatchesByArticle, createDraft } from '../../api/services';
import { extractErrorMessage } from '../../api/services';
import { useNavigate } from 'react-router-dom';
import { useAppSettings } from '../../hooks/useAppSettings';

export default function DraftEntry() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    useAppSettings();

    const form = useForm({
        initialValues: {
            location_id: '1',
            article_id: '',
            batch_id: '',
            quantity_kg: 0,
            client_event_id: '', // Will be set on mount
        },
        validate: {
            location_id: (val) => !val ? 'Location ID is required' : null,
            article_id: (val) => !val ? 'Article is required' : null,
            batch_id: (val) => !val ? 'Batch is required' : null,
            quantity_kg: (val) => val <= 0 ? 'Quantity must be greater than 0' : null,
            client_event_id: (val) => !val ? 'Event ID is required' : null,
        },
    });

    // Initialize UUID on mount
    useEffect(() => {
        if (!form.values.client_event_id) {
            form.setFieldValue('client_event_id', uuidv4());
        }
    }, []);

    // Regenerate UUID helper
    const regenerateUuid = () => form.setFieldValue('client_event_id', uuidv4());

    // Fetch Articles
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'], // active only
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map(a => ({
            value: a.id.toString(),
            label: `${a.article_no} - ${a.description}`,
            article_no: a.article_no
        })),
    });

    // Fetch Batches (dependent on Article)
    const selectedArticle = articlesQuery.data?.find(a => a.value === form.values.article_id);
    const batchesQuery = useQuery({
        queryKey: ['batches', selectedArticle?.article_no],
        queryFn: () => getBatchesByArticle(selectedArticle!.article_no),
        enabled: !!selectedArticle?.article_no,
    });

    const batchOptions = batchesQuery.data?.items.map(b => ({
        value: b.id.toString(),
        label: `${b.batch_code} ${b.expiry_date ? `(Exp: ${dayjs(b.expiry_date).format('DD.MM.YYYY')})` : ''}`
    })) || [];

    const selectedBatch = batchesQuery.data?.items.find(b => b.id.toString() === form.values.batch_id);
    const isBatchExpired = selectedBatch?.expiry_date && dayjs(selectedBatch.expiry_date).isBefore(dayjs());

    // Create Draft Mutation
    const mutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            return createDraft({
                location_id: parseInt(values.location_id),
                article_id: parseInt(values.article_id),
                batch_id: parseInt(values.batch_id),
                quantity_kg: values.quantity_kg,
                client_event_id: values.client_event_id
            });
        },
        onSuccess: (data) => {
            notifications.show({
                title: 'Draft Created',
                message: `Draft ID: ${data.id} created successfully.`,
                color: 'green',
                icon: <IconCheck size={16} />,
                autoClose: 10000,
            });

            // "Create Another" workflow:
            // Keep Location, Article, Batch. Reset Quantity and generate new UUID.
            form.setFieldValue('quantity_kg', 0);
            form.setFieldValue('client_event_id', uuidv4());

            // Invalidate drafts list so dashboard is up later
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
        },
        onError: (err) => {
            notifications.show({
                title: 'Creation Failed',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
            });
        }
    });

    return (
        <Container size="sm" py="xl">
            <Paper shadow="xs" p="xl" withBorder>
                <Title order={2} mb="md">Manual Weigh-In Entry</Title>
                <Text c="dimmed" mb="xl">Create a new weight draft. Entries will be pending approval.</Text>

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
                            onChange={(val) => {
                                form.setFieldValue('article_id', val || '');
                                form.setFieldValue('batch_id', ''); // Reset batch
                            }}
                            required
                        />

                        <Select
                            label="Batch"
                            placeholder={!form.values.article_id ? "Select an article first" : "Select batch"}
                            data={batchOptions}
                            searchable
                            disabled={!form.values.article_id || batchesQuery.isLoading}
                            {...form.getInputProps('batch_id')}
                            required
                            error={isBatchExpired ? 'Selected batch is EXPIRED!' : null}
                        />

                        {isBatchExpired && (
                            <Alert icon={<IconAlertTriangle size={16} />} title="Warning: Expired Batch" color="red" variant="filled">
                                This batch expired on {dayjs(selectedBatch.expiry_date).format('DD.MM.YYYY')}.
                                You can still proceed, but this will be flagged.
                            </Alert>
                        )}

                        <NumberInput
                            label="Quantity (kg)"
                            placeholder="0.00"
                            decimalScale={2}
                            fixedDecimalScale
                            min={0}
                            step={0.01}
                            {...form.getInputProps('quantity_kg')}
                            required
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

                        {mutation.isError && (
                            <Alert icon={<IconX size={16} />} title="Error" color="red">
                                {extractErrorMessage(mutation.error)}
                            </Alert>
                        )}

                        {/* Success/Navigation hint */}
                        {mutation.isSuccess && (
                            <Alert icon={<IconCheck size={16} />} title="Success" color="green" withCloseButton onClose={mutation.reset}>
                                Draft created! You can fill the form again for another entry, or <Anchor onClick={() => navigate('/drafts')} fw={700}>Go to Approvals</Anchor>.
                            </Alert>
                        )}

                        <Group mt="md" grow>
                            <Button type="submit" loading={mutation.isPending}>
                                Submit Entry
                            </Button>
                        </Group>
                    </Stack>
                </form>
            </Paper>
        </Container>
    );
}
