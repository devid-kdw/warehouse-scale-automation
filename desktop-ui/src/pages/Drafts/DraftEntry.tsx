import { useState, useEffect, useRef } from 'react';
import {
    Container, Paper, Title, Select, TextInput, NumberInput,
    Button, Group, Stack, Alert, ActionIcon, Tooltip, Text, Anchor, Tabs,
    SegmentedControl
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
import { useAuth } from '../../hooks/useAuth';
import { getDrafts } from '../../api/services';
import { Table, Badge } from '@mantine/core';
import BulkDraftEntry from './BulkDraftEntry';
import { isAdmin } from '../../api/auth';

export default function DraftEntry() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    useAppSettings();
    const { user } = useAuth();
    const [qtyMode, setQtyMode] = useState<'manual' | 'scale'>(
        (localStorage.getItem('draftEntry.qtyMode') as 'manual' | 'scale') || 'manual'
    );
    const barcodeBuffer = useRef('');
    const lastKeyTime = useRef(0);

    // Fetch My Drafts
    const draftsQuery = useQuery({
        queryKey: ['drafts', 'my'],
        queryFn: () => getDrafts(), // Fetch all, filtered client side
        select: (data) => data.items.filter(d => d.created_by_user_id === user?.id).sort((a, b) => b.id - a.id).slice(0, 5) // Last 5
    });

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

    // Initialize UUID on mount + Barcode Listener
    useEffect(() => {
        if (!form.values.client_event_id) {
            form.setFieldValue('client_event_id', uuidv4());
        }

        const handleGlobalKeyDown = (e: KeyboardEvent) => {
            const active = document.activeElement;
            const isInput = active?.tagName === 'INPUT' || active?.tagName === 'TEXTAREA';

            // Only capture if NOT in an input (safety requirement)
            if (isInput) {
                // Special case: if it's the article select's search input, we might still want to capture?
                // But prompt says: "Do NOT override user if they are explicitly typing in a textarea or input."
                // So we stick to safety.
                return;
            }

            const now = Date.now();
            if (now - lastKeyTime.current > 50) {
                barcodeBuffer.current = '';
            }
            lastKeyTime.current = now;

            if (e.key === 'Enter') {
                if (barcodeBuffer.current.length >= 4) {
                    processBarcode(barcodeBuffer.current);
                }
                barcodeBuffer.current = '';
            } else if (e.key.length === 1) {
                barcodeBuffer.current += e.key;
            }
        };

        window.addEventListener('keydown', handleGlobalKeyDown);
        return () => window.removeEventListener('keydown', handleGlobalKeyDown);
    }, []);

    const processBarcode = async (code: string) => {
        try {
            // Find article by barcode/alias
            notifications.show({ title: 'Barcode Scanned', message: `Searching for: ${code}`, color: 'blue', loading: true, id: 'barcode-scan' });
            const article = await getArticles('true').then(res =>
                res.items.find(a => a.article_no === code)
            );

            if (article) {
                form.setFieldValue('article_id', article.id.toString());
                notifications.update({ id: 'barcode-scan', title: 'Success', message: `Selected: ${article.article_no}`, color: 'green', loading: false });
            } else {
                notifications.update({ id: 'barcode-scan', title: 'Not Found', message: `Article ${code} unknown.`, color: 'orange', loading: false });
            }
        } catch (err) {
            notifications.update({ id: 'barcode-scan', title: 'Error', message: 'Barcode resolution failed', color: 'red', loading: false });
        }
    };

    useEffect(() => {
        localStorage.setItem('draftEntry.qtyMode', qtyMode);
    }, [qtyMode]);

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
            <Title order={2} mb="md">Manual Weigh-In Entry</Title>
            <Text c="dimmed" mb="xl">Create new weight drafts. Entries will be pending approval.</Text>

            {isAdmin() ? (
                <Tabs defaultValue="single" mb="xl">
                    <Tabs.List mb="md">
                        <Tabs.Tab value="single">Single Entry</Tabs.Tab>
                        <Tabs.Tab value="bulk">Bulk Entry (Admin)</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="single">
                        <Paper shadow="xs" p="xl" withBorder>
                            <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                                <Stack>
                                    <Group justify="space-between">
                                        <TextInput
                                            label="Location ID"
                                            description="Default is 1 (Main Scale)."
                                            {...form.getInputProps('location_id')}
                                            style={{ flex: 1 }}
                                        />
                                        <Stack gap={2}>
                                            <Text size="sm" fw={500}>Entry Mode</Text>
                                            <SegmentedControl
                                                value={qtyMode}
                                                onChange={(val: any) => setQtyMode(val)}
                                                data={[
                                                    { label: 'Manual', value: 'manual' },
                                                    { label: 'Scale', value: 'scale' },
                                                ]}
                                            />
                                        </Stack>
                                    </Group>

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
                                        placeholder={qtyMode === 'scale' ? "Waiting for scale..." : "0.00"}
                                        decimalScale={2}
                                        fixedDecimalScale
                                        min={0}
                                        step={0.01}
                                        {...form.getInputProps('quantity_kg')}
                                        required
                                        readOnly={qtyMode === 'scale'}
                                        variant={qtyMode === 'scale' ? 'filled' : 'default'}
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
                    </Tabs.Panel>

                    <Tabs.Panel value="bulk">
                        <Paper shadow="xs" p="xl" withBorder>
                            <BulkDraftEntry />
                        </Paper>
                    </Tabs.Panel>
                </Tabs>
            ) : (
                <Paper shadow="xs" p="xl" withBorder>
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
            )}

            <Paper shadow="xs" p="xl" mt="xl" withBorder>
                <Title order={3} mb="md">My Recent Drafts</Title>
                {draftsQuery.isLoading ? (
                    <Text size="sm">Loading drafts...</Text>
                ) : draftsQuery.data && draftsQuery.data.length > 0 ? (
                    <Table>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Article</Table.Th>
                                <Table.Th>Batch</Table.Th>
                                <Table.Th>Qty</Table.Th>
                                <Table.Th>Status</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {draftsQuery.data.map(draft => (
                                <Table.Tr key={draft.id}>
                                    <Table.Td>{draft.id}</Table.Td>
                                    <Table.Td>{draft.article_id}</Table.Td>
                                    <Table.Td>{draft.batch_id}</Table.Td>
                                    <Table.Td>{draft.quantity_kg}</Table.Td>
                                    <Table.Td>
                                        <Badge color={draft.status === 'APPROVED' ? 'green' : (draft.status === 'REJECTED' ? 'red' : 'blue')}>
                                            {draft.status}
                                        </Badge>
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                ) : (
                    <Text c="dimmed" size="sm">No recent drafts found.</Text>
                )}
            </Paper>
        </Container >
    );
}
