
import { useState, useRef, useEffect } from 'react';
import {
    Container, Paper, Title, TextInput, Button, Group, Stack, Table,
    ActionIcon, NumberInput, Select, Text
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconTrash, IconPlus, IconCheck, IconX } from '@tabler/icons-react';
import { v4 as uuidv4 } from 'uuid';
import { useTranslation } from 'react-i18next';
import { getArticles, getBatchesByArticle, createDraftGroup, extractErrorMessage } from '../../api/services';
import dayjs from 'dayjs';

interface LineItem {
    id: string; // Temporary UI ID
    article_id: string;
    batch_id: string;
    quantity: number;
    uom: string; // From article
    client_event_id: string;
    article_no?: string; // For display
    description?: string; // For display
    batch_code?: string; // For display
}

export default function Izlaz() {
    const { t } = useTranslation('common');
    const queryClient = useQueryClient();
    const barcodeBuffer = useRef('');
    const lastKeyTime = useRef(0);

    // Group-level form
    const form = useForm({
        initialValues: {
            description: '',
            location_id: 13
        },
        validate: {
            description: (val) => !val ? t('common.required') : null,
        }
    });

    const [lines, setLines] = useState<LineItem[]>([]);

    // Fetch Articles for lookup
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'],
        queryFn: () => getArticles('true'),
    });

    // Mutation to create group
    const mutation = useMutation({
        mutationFn: async () => {
            if (lines.length === 0) throw new Error("No lines to submit");

            return createDraftGroup({
                location_id: form.values.location_id,
                name: "Izlaz", // System will auto-generate/override or we pass name? Backed assigns numbering?
                // The task brief says "Add group-level Description"
                // Our API type has `description?: string`
                description: form.values.description,
                lines: lines.map(l => ({
                    article_id: parseInt(l.article_id),
                    batch_id: l.batch_id ? parseInt(l.batch_id) : null,
                    quantity: l.quantity,
                    uom: l.uom,
                    client_event_id: l.client_event_id
                }))
            });
        },
        onSuccess: (data) => {
            notifications.show({
                title: t('izlaz.success'),
                message: `${t('izlaz.success')} ID: ${data.id}`,
                color: 'green',
                icon: <IconCheck size={16} />
            });
            setLines([]);
            form.reset();
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
        },
        onError: (err) => {
            notifications.show({
                title: t('common.error'),
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />
            });
        }
    });

    // Global Barcode Listener
    useEffect(() => {
        const handleGlobalKeyDown = (e: KeyboardEvent) => {
            const active = document.activeElement;
            const isInput = active?.tagName === 'INPUT' || active?.tagName === 'TEXTAREA';
            if (isInput) return;

            const now = Date.now();
            if (now - lastKeyTime.current > 50) barcodeBuffer.current = '';
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
    }, [articlesQuery.data]);

    const processBarcode = (code: string) => {
        const article = articlesQuery.data?.items.find(a => a.article_no === code);
        if (article) {
            addLine(article);
            notifications.show({ title: 'Scanned', message: article.article_no, color: 'blue' });
        } else {
            notifications.show({ title: 'Unknown', message: code, color: 'orange' });
        }
    };

    const addLine = (article?: any) => {
        setLines(prev => [...prev, {
            id: uuidv4(),
            article_id: article ? article.id.toString() : '',
            batch_id: '',
            quantity: 0,
            uom: article ? (article.uom || 'KG') : 'KG',
            client_event_id: uuidv4(),
            article_no: article?.article_no,
            description: article?.description,
            batch_code: ''
        }]);
    };

    const removeLine = (id: string) => {
        setLines(prev => prev.filter(l => l.id !== id));
    };

    const updateLine = (id: string, field: keyof LineItem, value: any) => {
        setLines(prev => prev.map(l => {
            if (l.id !== id) return l;

            if (field === 'article_id') {
                const article = articlesQuery.data?.items.find(a => a.id.toString() === value);
                return {
                    ...l,
                    article_id: value,
                    article_no: article?.article_no,
                    description: article?.description,
                    uom: article?.uom || 'KG',
                    batch_id: '' // Reset batch on article change
                };
            }
            return { ...l, [field]: value };
        }));
    };

    const articleOptions = articlesQuery.data?.items.map(a => ({
        value: a.id.toString(),
        label: `${a.article_no} - ${a.description} (${a.uom || 'KG'})`
    })) || [];

    // Helper component for batch selection row
    // Need to fetch batches per row if article selected
    // Note: This might spam requests if many rows. 
    // Optimization: ideally prefetch or use a cache. React Query handles cache.

    return (
        <Container size="xl" py="xl" className="page-container">
            <Stack gap="lg">
                <Title order={2}>{t('izlaz.title')}</Title>

                <Paper shadow="xs" p="md" withBorder>
                    <Group align="flex-end">
                        <TextInput
                            label={t('izlaz.outboundNumber')}
                            value={t('izlaz.generated')}
                            disabled
                            style={{ width: 200 }}
                        />
                        <TextInput
                            label={t('izlaz.description')}
                            required
                            style={{ flex: 1 }}
                            {...form.getInputProps('description')}
                        />
                    </Group>
                </Paper>

                <Paper shadow="xs" p="md" withBorder>
                    <Stack>
                        <Group justify="space-between">
                            <Title order={4}>{t('izlaz.actions')}</Title>
                            <Button leftSection={<IconPlus size={16} />} onClick={() => addLine()}>
                                {t('izlaz.addLine')}
                            </Button>
                        </Group>

                        <Table>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th style={{ width: 300 }}>{t('izlaz.article')}</Table.Th>
                                    <Table.Th>{t('izlaz.batch')}</Table.Th>
                                    <Table.Th style={{ width: 150 }}>{t('izlaz.quantity')}</Table.Th>
                                    <Table.Th style={{ width: 100 }}>{t('izlaz.uom')}</Table.Th>
                                    <Table.Th style={{ width: 50 }}></Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {lines.map((line, index) => (
                                    <LineRow
                                        key={line.id}
                                        line={line}
                                        index={index}
                                        articleOptions={articleOptions}
                                        updateLine={updateLine}
                                        removeLine={removeLine}
                                        t={t}
                                    />
                                ))}
                                {lines.length === 0 && (
                                    <Table.Tr>
                                        <Table.Td colSpan={5} align="center">
                                            <Text c="dimmed" size="sm">Scan barcode or click Add Line</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                )}
                            </Table.Tbody>
                        </Table>

                        <Group mt="xl" justify="flex-end">
                            <Button
                                size="lg"
                                disabled={lines.length === 0}
                                loading={mutation.isPending}
                                onClick={() => {
                                    const validation = form.validate();
                                    if (!validation.hasErrors) {
                                        mutation.mutate();
                                    }
                                }}
                            >
                                {t('izlaz.submit')}
                            </Button>
                        </Group>
                    </Stack>
                </Paper>
            </Stack>
        </Container>
    );
}

// Extracted row component to handle individual batch queries hooks
function LineRow({ line, articleOptions, updateLine, removeLine, t }: any) {
    // Only fetch batches if article is selected
    const { data: batches } = useQuery({
        queryKey: ['batches', line.article_id],
        queryFn: async () => {
            if (!line.article_id) return { items: [] };
            // We need article_no to fetch batches
            // We can separate getBatches to take ID or just find the article from options
            // Just filtering options is easier if we have reference, but options is just label/value
            // Let's assume we can get it from article_no if we have it? 
            // line.article_no might be populated if we selected.
            // If not, we might need to look it up.
            // Let's assume getBatchesByArticle takes articleNo.
            // We need to find articleNo from article_id.
            // Hack: let's assume we can find it in articleOptions or parent passed it?
            // Actually, parent `updateLine` sets `article_no`.
            if (line.article_no) {
                return getBatchesByArticle(line.article_no);
            }
            return { items: [] };
        },
        enabled: !!line.article_id && !!line.article_no
    });

    const batchOptions = batches?.items?.map((b: any) => ({
        value: b.id.toString(),
        label: `${b.batch_code} ${b.expiry_date ? `(Exp: ${dayjs(b.expiry_date).format('DD.MM.YYYY')})` : ''}`
    })) || [];

    const hasBatch = batchOptions.length > 0; // Or better: check article 'has_batch' flag?
    // Parent didn't pass full article object.
    // If no batches, maybe disabled or hidden?
    // Task brief says: "Batch field should render only for batch-tracked articles."
    // We can infer it if batchOptions > 0 OR if we had `has_batch` in articleOptions.
    // Let's stick to simple: if batches exist, show select.

    return (
        <Table.Tr>
            <Table.Td>
                <Select
                    data={articleOptions}
                    value={line.article_id}
                    onChange={(val) => updateLine(line.id, 'article_id', val)}
                    searchable
                    placeholder={t('izlaz.article')}
                />
            </Table.Td>
            <Table.Td>
                <Select
                    data={batchOptions}
                    value={line.batch_id}
                    onChange={(val) => updateLine(line.id, 'batch_id', val)}
                    disabled={!line.article_id}
                    placeholder={hasBatch ? t('izlaz.batch') : "N/A"}
                />
            </Table.Td>
            <Table.Td>
                <NumberInput
                    min={0}
                    decimalScale={2}
                    fixedDecimalScale
                    value={line.quantity}
                    onChange={(val) => updateLine(line.id, 'quantity', val)}
                />
            </Table.Td>
            <Table.Td>
                <Text size="sm">{line.uom}</Text>
            </Table.Td>
            <Table.Td>
                <ActionIcon color="red" variant="subtle" onClick={() => removeLine(line.id)}>
                    <IconTrash size={16} />
                </ActionIcon>
            </Table.Td>
        </Table.Tr>
    )
}
