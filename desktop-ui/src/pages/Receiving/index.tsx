
import {
    Container, Paper, Title, Select, TextInput, NumberInput,
    Button, Group, Stack, Alert, Textarea, Text
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconCheck, IconX, IconPackageImport } from '@tabler/icons-react';
import dayjs from 'dayjs';
import { getArticles, receiveStock, extractErrorMessage } from '../../api/services';
import { useAppSettings } from '../../hooks/useAppSettings';

export default function Receiving() {
    const queryClient = useQueryClient();
    useAppSettings();

    const form = useForm({
        initialValues: {
            article_id: '',
            batch_code: '',
            quantity_kg: 0,
            expiry_date: null as Date | null,
            note: '',
            // Hidden fields
            location_id: 1 // Default to 1
        },
        validate: {
            article_id: (val) => !val ? 'Article is required' : null,
            batch_code: (val) => {
                if (!val) return 'Batch code is required';
                if (!/^\d{4,5}$|^\d{9,12}$/.test(val)) {
                    return 'Invalid format. Must be 4-5 (Mankiewicz) or 9-12 (Akzo) digits.';
                }
                return null;
            },
            quantity_kg: (val) => val <= 0 ? 'Quantity must be greater than 0' : null,
            expiry_date: (val) => !val ? 'Expiry date is required' : null,
        },
    });

    // Fetch Articles
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'],
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map(a => ({
            value: a.id.toString(),
            label: `${a.article_no} - ${a.description}`,
            article_no: a.article_no
        })),
    });

    // Receive Mutation
    const mutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            return receiveStock({
                article_id: parseInt(values.article_id),
                batch_code: values.batch_code,
                quantity_kg: values.quantity_kg,
                expiry_date: values.expiry_date ? dayjs(values.expiry_date).format('YYYY-MM-DD') : '',
                note: values.note,
                location_id: values.location_id
            });
        },
        onSuccess: (data) => {
            notifications.show({
                title: 'Stock Received',
                message: `Received ${data.quantity_received}kg. ${data.batch_created ? 'New Batch created.' : 'Existing Batch updated.'}`,
                color: 'green',
                icon: <IconCheck size={16} />,
                autoClose: 5000,
            });

            // Invalidate queries
            queryClient.invalidateQueries({ queryKey: ['inventorySummary'] });
            queryClient.invalidateQueries({ queryKey: ['transactions'] });
            queryClient.invalidateQueries({ queryKey: ['batches'] });

            // Reset form but KEEP Article
            form.setFieldValue('batch_code', '');
            form.setFieldValue('quantity_kg', 0);
            form.setFieldValue('expiry_date', null);
            form.setFieldValue('note', '');
            // article_id remains set
        },
        onError: (err: any) => {
            // Check for specific error codes if needed, e.g. BATCH_EXPIRY_MISMATCH
            // The extractErrorMessage helper usually handles details
            notifications.show({
                title: 'Receive Failed',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
                autoClose: 10000,
            });
        }
    });

    return (
        <Container size="sm" py="xl">
            <Paper shadow="xs" p="xl" withBorder>
                <Title order={2} mb="md">
                    <Group>
                        <IconPackageImport size={28} />
                        Receive Stock
                    </Group>
                </Title>
                <Text c="dimmed" mb="xl">
                    Add new inventory to the warehouse. Requires Admin privileges.
                </Text>

                <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                    <Stack>
                        <Select
                            label="Article"
                            placeholder="Select article"
                            data={articlesQuery.data || []}
                            searchable
                            nothingFoundMessage="No articles found"
                            disabled={articlesQuery.isLoading}
                            {...form.getInputProps('article_id')}
                            required
                        />

                        <TextInput
                            label="Batch Code"
                            placeholder="e.g. 12345 or 1234567890"
                            description="4-5 digits (Mankiewicz) or 9-12 digits (Akzo)"
                            {...form.getInputProps('batch_code')}
                            required
                        />

                        <DateInput
                            label="Expiry Date"
                            placeholder="Select date"
                            valueFormat="DD.MM.YYYY"
                            minDate={new Date()} // Optional: prevent receiving already expired? Backend allows it but warns.
                            // User requirement says it's required.
                            {...form.getInputProps('expiry_date')}
                            required
                        />

                        <NumberInput
                            label="Quantity (kg)"
                            placeholder="0.00"
                            decimalScale={2}
                            fixedDecimalScale
                            min={0.01}
                            step={0.01}
                            {...form.getInputProps('quantity_kg')}
                            required
                        />

                        <Textarea
                            label="Note"
                            placeholder="Optional reception note"
                            {...form.getInputProps('note')}
                        />

                        {mutation.isError && (
                            <Alert icon={<IconX size={16} />} title="Error" color="red">
                                {extractErrorMessage(mutation.error)}
                            </Alert>
                        )}

                        <Group mt="md" grow>
                            <Button type="submit" loading={mutation.isPending}>
                                Receive Stock
                            </Button>
                        </Group>
                    </Stack>
                </form>
            </Paper>
        </Container>
    );
}
