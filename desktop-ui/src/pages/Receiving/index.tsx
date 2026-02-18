
import {
    Container, Paper, Title, Select, TextInput, NumberInput,
    Button, Group, Stack, Textarea, Text, LoadingOverlay
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconCheck, IconX, IconPackageImport, IconInfoCircle } from '@tabler/icons-react';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import { getArticles, receiveStock, extractErrorMessage, getBatchesByArticle } from '../../api/services';
import { listOrders } from '../../api/orders';
import { ReceiptHistoryList } from '../../components/ReceiptHistoryList';

export default function Receiving() {
    const { t } = useTranslation('common');
    const queryClient = useQueryClient();

    // Fetch Articles
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'],
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map(a => ({
            value: a.id.toString(),
            label: `${a.article_no} - ${a.description}`,
            article_no: a.article_no,
            is_paint: a.is_paint,
            // Fallback for has_batch if not yet in API response type locally
            has_batch: (a as any).has_batch ?? (a.is_paint !== false)
        })),
    });

    // Fetch Orders for linking
    const ordersQuery = useQuery({
        queryKey: ['orders', 'OPEN'],
        queryFn: () => listOrders('OPEN'),
    });

    const form = useForm({
        initialValues: {
            article_id: '',
            delivery_note_number: '',
            order_id: '', // Helper to filter lines
            order_line_id: '',
            batch_code: '',
            quantity: 0,
            uom: 'KG', // Default
            expiry_date: null as Date | null,
            note: '',
            location_id: 13
        },
        validate: {
            article_id: (val) => !val ? t('common.required') : null,
            delivery_note_number: (val) => !val ? t('common.required') : null,
            quantity: (val) => val <= 0 ? `${t('receiving.quantity')} > 0` : null,
            uom: (val) => (val !== 'KG' && val !== 'L') ? t('receiving.unsupportedUom', { uom: val }) : null,
            note: (val, values) => (!values.order_line_id && !val) ? t('receiving.adHocNote') : null,
            batch_code: (val, values) => {
                const article = articlesQuery.data?.find(a => a.value === values.article_id);
                const hasBatch = article?.has_batch;

                if (!hasBatch) return null;
                if (!val) return t('common.required');
                if (!/^\d{4,5}$|^\d{9,12}$/.test(val)) {
                    return 'Invalid format (4-5 or 9-12 digits)';
                }
                return null;
            },
            expiry_date: (val, values) => {
                const article = articlesQuery.data?.find(a => a.value === values.article_id);
                const hasBatch = article?.has_batch;
                if (!hasBatch) return null;
                return !val ? t('common.required') : null;
            },
        },
    });

    const selectedArticle = articlesQuery.data?.find(a => a.value === form.values.article_id);
    const hasBatch = selectedArticle?.has_batch;

    // Fetch Batches for visual feedback
    const batchesQuery = useQuery({
        queryKey: ['batches', form.values.article_id],
        queryFn: () => {
            if (!selectedArticle) return { items: [], total: 0 };
            return getBatchesByArticle(selectedArticle.article_no);
        },
        enabled: !!form.values.article_id && !!hasBatch,
    });

    const existingBatch = batchesQuery.data?.items.find(b => b.batch_code === form.values.batch_code);
    const isNewBatch = form.values.batch_code.length >= 4 && !existingBatch && hasBatch;

    const orderOptions = ordersQuery.data?.items.map(o => ({
        value: o.id.toString(),
        label: `${o.order_number} - ${o.supplier_name || 'Unknown'}`
    })) || [];

    const selectedOrder = ordersQuery.data?.items.find(o => o.id.toString() === form.values.order_id);
    const lineOptions = selectedOrder?.lines
        .filter(l => l.status === 'OPEN')
        .map(l => ({
            value: l.id.toString(),
            label: `${l.article_no} - ${l.ordered_qty} ${l.uom} (Recv: ${l.received_qty})`
        })) || [];

    const mutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            return receiveStock({
                article_id: parseInt(values.article_id),
                delivery_note_number: values.delivery_note_number,
                order_line_id: values.order_line_id ? parseInt(values.order_line_id) : undefined,
                quantity: values.quantity,
                uom: values.uom,
                batch_code: hasBatch ? values.batch_code : undefined,
                expiry_date: (hasBatch && values.expiry_date)
                    ? dayjs(values.expiry_date).format('YYYY-MM-DD')
                    : undefined,
                note: values.note,
                location_id: values.location_id
            });
        },
        onSuccess: (data) => {
            const qty = data.quantity_received || form.values.quantity; // Fallback if API hasn't updated response type locally
            notifications.show({
                title: t('common.success'),
                message: `${t('receiving.receiveStock')} OK: ${qty} ${form.values.uom}`,
                color: 'green',
                icon: <IconCheck size={16} />,
            });

            queryClient.invalidateQueries({ queryKey: ['inventorySummary'] });
            queryClient.invalidateQueries({ queryKey: ['receiptHistory'] });
            queryClient.invalidateQueries({ queryKey: ['orders'] });

            // Invalidate batches if we created one
            if (hasBatch) {
                queryClient.invalidateQueries({ queryKey: ['batches'] });
            }

            form.setFieldValue('quantity', 0);
            form.setFieldValue('batch_code', '');
            form.setFieldValue('expiry_date', null);
            form.setFieldValue('note', '');
        },
        onError: (err: any) => {
            notifications.show({
                title: t('common.error'),
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
            });
        }
    });

    return (
        <Container size="md" py="xl" className="page-container">
            <Stack gap="xl">
                <Paper shadow="xs" p="xl" withBorder style={{ position: 'relative' }}>
                    <LoadingOverlay visible={mutation.isPending} overlayProps={{ radius: "sm", blur: 2 }} />

                    <Title order={2} mb="md">
                        <Group>
                            <IconPackageImport size={28} />
                            {t('receiving.title')}
                        </Group>
                    </Title>

                    <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                        <Stack>
                            <TextInput
                                label={t('receiving.deliveryNote')}
                                required
                                {...form.getInputProps('delivery_note_number')}
                            />

                            <Group grow>
                                <Select
                                    label={t('orders.title')}
                                    placeholder="Select order (optional)"
                                    data={orderOptions}
                                    searchable
                                    clearable
                                    {...form.getInputProps('order_id')}
                                    onChange={(val) => {
                                        form.setFieldValue('order_id', val || '');
                                        form.setFieldValue('order_line_id', '');
                                    }}
                                />
                                <Select
                                    label={t('receiving.orderLine')}
                                    placeholder={t('receiving.selectOrderLine')}
                                    data={lineOptions}
                                    disabled={!form.values.order_id}
                                    searchable
                                    clearable
                                    {...form.getInputProps('order_line_id')}
                                    onChange={(val) => {
                                        form.setFieldValue('order_line_id', val || '');
                                        if (val && selectedOrder) {
                                            const line = selectedOrder.lines.find(l => l.id.toString() === val);
                                            if (line) {
                                                const article = articlesQuery.data?.find(a => a.article_no === line.article_no);
                                                if (article) {
                                                    form.setFieldValue('article_id', article.value);
                                                    form.setFieldValue('uom', line.uom as string);
                                                }
                                            }
                                        }
                                    }}
                                />
                            </Group>

                            <Select
                                label={t('nav.articles')}
                                data={articlesQuery.data || []}
                                searchable
                                required
                                {...form.getInputProps('article_id')}
                                onChange={(val) => {
                                    form.setFieldValue('article_id', val || '');
                                    form.setFieldValue('batch_code', '');
                                    form.setFieldValue('expiry_date', null);
                                }}
                            />

                            {hasBatch && (
                                <>
                                    <TextInput
                                        label={t('receiving.batchCode')}
                                        required
                                        {...form.getInputProps('batch_code')}
                                        rightSection={existingBatch ? <IconCheck color="green" size={16} /> : (isNewBatch ? <IconInfoCircle color="blue" size={16} /> : null)}
                                    />
                                    {isNewBatch && <Text size="xs" c="blue" mt={-10}>New batch will be created</Text>}

                                    <DateInput
                                        label={t('receiving.expiryDate')}
                                        required
                                        valueFormat="DD.MM.YYYY"
                                        {...form.getInputProps('expiry_date')}
                                    />
                                </>
                            )}

                            <Group grow>
                                <NumberInput
                                    label={t('receiving.quantity')}
                                    decimalScale={2}
                                    step={0.01}
                                    required
                                    min={0.01}
                                    {...form.getInputProps('quantity')}
                                />
                                <Select
                                    label={t('receiving.uom')}
                                    data={['KG', 'L']}
                                    required
                                    {...form.getInputProps('uom')}
                                />
                            </Group>

                            <Textarea
                                label="Note"
                                placeholder={form.values.order_line_id ? 'Optional' : 'Required for ad-hoc'}
                                required={!form.values.order_line_id}
                                {...form.getInputProps('note')}
                            />

                            <Button type="submit" loading={mutation.isPending} fullWidth>
                                {t('receiving.receiveStock')}
                            </Button>
                        </Stack>
                    </form>
                </Paper>

                <Stack>
                    <Title order={3}>{t('receiving.recentReceipts')}</Title>
                    <ReceiptHistoryList />
                </Stack>
            </Stack>
        </Container>
    );
}
