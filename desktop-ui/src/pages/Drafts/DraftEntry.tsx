
import { useState, useEffect, useRef } from 'react';
import {
    Container, Paper, Title, Select,
    Button, Group, Stack, Alert, ActionIcon, Tooltip, Text, Anchor,
    SegmentedControl, NumberInput
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconRefresh, IconCheck, IconX, IconAlertTriangle } from '@tabler/icons-react';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { getArticles, getBatchesByArticle, createDraft, extractErrorMessage } from '../../api/services';

export default function DraftEntry() {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [qtyMode, setQtyMode] = useState<'manual' | 'scale'>(
        (localStorage.getItem('draftEntry.qtyMode') as 'manual' | 'scale') || 'scale'
    );
    const barcodeBuffer = useRef('');
    const lastKeyTime = useRef(0);

    useEffect(() => {
        localStorage.setItem('draftEntry.qtyMode', qtyMode);
    }, [qtyMode]);

    const form = useForm({
        initialValues: {
            location_id: 13, // Fixed to 13
            article_id: '',
            batch_id: '',
            quantity: 0,
            client_event_id: '', // Will be set on mount
        },
        validate: {
            article_id: (val) => !val ? t('common.required') : null,
            batch_id: (val) => !val ? t('common.required') : null,
            quantity: (val) => val <= 0 ? `${t('entries.quantity')} > 0` : null,
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

            if (isInput) return;

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
            notifications.show({ title: 'Barcode Scanned', message: `Searching for: ${code}`, color: 'blue', loading: true, id: 'barcode-scan' });
            const articles = await getArticles('true');
            const article = articles.items.find(a => a.article_no === code);

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

    const regenerateUuid = () => form.setFieldValue('client_event_id', uuidv4());

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

    // Fetch Batches
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

    const mutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            return createDraft({
                location_id: values.location_id,
                article_id: parseInt(values.article_id),
                batch_id: parseInt(values.batch_id),
                quantity: values.quantity,
                client_event_id: values.client_event_id
            });
        },
        onSuccess: (data) => {
            notifications.show({
                title: t('entries.success'),
                message: t('entries.successMsg', { id: data.id }),
                color: 'green',
                icon: <IconCheck size={16} />,
                autoClose: 5000,
            });

            // Reset only quantity/event, keep article/batch for rapid entry
            form.setFieldValue('quantity', 0);
            form.setFieldValue('client_event_id', uuidv4());

            queryClient.invalidateQueries({ queryKey: ['drafts'] });
        },
        onError: (err) => {
            notifications.show({
                title: t('common.error'),
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
            });
        }
    });

    return (
        <Container size="sm" py="xl" className="page-container">
            <Stack gap="xl">
                <Group justify="space-between" align="center">
                    <Title order={2}>{t('entries.title')}</Title>
                    <SegmentedControl
                        value={qtyMode}
                        onChange={(val: any) => setQtyMode(val)}
                        data={[
                            { label: t('entries.scale'), value: 'scale' },
                            { label: t('entries.manual'), value: 'manual' },
                        ]}
                    />
                </Group>

                <Paper shadow="xs" p="xl" withBorder>
                    <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                        <Stack gap="lg">
                            <Select
                                label={t('entries.article')}
                                placeholder={t('entries.selectArticle')}
                                data={articlesQuery.data || []}
                                searchable
                                nothingFoundMessage="No articles found"
                                disabled={articlesQuery.isLoading}
                                {...form.getInputProps('article_id')}
                                onChange={(val) => {
                                    form.setFieldValue('article_id', val || '');
                                    form.setFieldValue('batch_id', '');
                                }}
                                required
                            />

                            <Select
                                label={t('entries.batch')}
                                placeholder={!form.values.article_id ? t('entries.selectArticle') : t('entries.selectBatch')}
                                data={batchOptions}
                                searchable
                                disabled={!form.values.article_id || batchesQuery.isLoading}
                                {...form.getInputProps('batch_id')}
                                required
                                error={isBatchExpired ? t('entries.expiredBatch') : null}
                            />

                            {isBatchExpired && (
                                <Alert icon={<IconAlertTriangle size={16} />} title={t('entries.expiredBatch')} color="red" variant="filled">
                                    {t('entries.expiredBatchDesc', { date: dayjs(selectedBatch.expiry_date).format('DD.MM.YYYY') })}
                                </Alert>
                            )}

                            <NumberInput
                                label={t('entries.quantity')}
                                placeholder={qtyMode === 'scale' ? t('entries.waitingForScale') : "0.00"}
                                decimalScale={2}
                                fixedDecimalScale
                                min={0}
                                step={0.01}
                                {...form.getInputProps('quantity')}
                                required
                                readOnly={qtyMode === 'scale'}
                                variant={qtyMode === 'scale' ? 'filled' : 'default'}
                                rightSection={<Text size="xs" c="dimmed">KG</Text>}
                            />

                            {/* Hidden Client Event ID for idempotency */}
                            <Tooltip label="Debug: Regenerate UUID">
                                <ActionIcon variant="subtle" size="xs" color="gray" onClick={regenerateUuid} style={{ alignSelf: 'flex-end' }}>
                                    <IconRefresh size={12} />
                                </ActionIcon>
                            </Tooltip>

                            <Button type="submit" loading={mutation.isPending} fullWidth size="md">
                                {t('entries.submit')}
                            </Button>

                            {mutation.isSuccess && (
                                <Alert icon={<IconCheck size={16} />} title={t('common.success')} color="green" withCloseButton onClose={mutation.reset}>
                                    {t('entries.successMsg', { id: '...' })}{' '}
                                    <Anchor onClick={() => navigate('/drafts')} fw={700}>
                                        {t('entries.goToApprovals')}
                                    </Anchor>
                                </Alert>
                            )}
                        </Stack>
                    </form>
                </Paper>
            </Stack>
        </Container>
    );
}
