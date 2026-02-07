import { useEffect, useRef } from 'react';
import {
    Table, TextInput, NumberInput, ActionIcon, Button,
    Group, Select, Stack, Tooltip, Badge
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconTrash, IconPlus, IconCheck, IconX, IconArrowRight, IconCopy } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getArticles, getBatchesByArticle, createDraftGroup, approveDraftGroup, extractErrorMessage } from '../../api/services';
import { notifications } from '@mantine/notifications';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';

export default function BulkDraftEntry() {
    const queryClient = useQueryClient();

    // Fetch Articles for lookup
    const articlesQuery = useQuery({
        queryKey: ['articles', 'true'],
        queryFn: () => getArticles('true'),
        select: (data) => data.items.map(a => ({
            value: a.id.toString(),
            label: `${a.article_no} - ${a.description}`,
            article_no: a.article_no,
            description: a.description,
            manufacturer: a.manufacturer,
            uom: a.uom,
            is_paint: a.is_paint
        })),
    });

    const form = useForm({
        initialValues: {
            name: '',
            lines: [
                { article_id: '', batch_id: '', quantity_kg: 0, note: '', client_event_id: uuidv4() }
            ]
        },
        validate: {
            lines: {
                article_id: (val) => !val ? 'Required' : null,
                batch_id: (val, values, path) => {
                    const index = parseInt(path.split('.')[1]);
                    const articleId = values.lines[index].article_id;
                    const article = articlesQuery.data?.find(a => a.value === articleId);
                    const isConsumable = article && article.is_paint === false;
                    if (isConsumable) return null;
                    return !val ? 'Required' : null;
                },
                quantity_kg: (val) => val <= 0 ? 'Must be > 0' : null,
            }
        }
    });

    const createMutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            return createDraftGroup({
                name: values.name || undefined,
                lines: values.lines.map(l => ({
                    article_id: parseInt(l.article_id),
                    batch_id: l.batch_id ? parseInt(l.batch_id) : null,
                    quantity_kg: l.quantity_kg,
                    note: l.note,
                    client_event_id: l.client_event_id
                }))
            });
        },
        onSuccess: (data) => {
            notifications.show({
                title: 'Draft Group Created',
                message: `Group "${data.name}" created with ${data.line_count} items.`,
                color: 'green',
                icon: <IconCheck size={16} />
            });
            form.reset();
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
        },
        onError: (err) => {
            notifications.show({
                title: 'Error',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />
            });
        }
    });

    const approveMutation = useMutation({
        mutationFn: async (values: typeof form.values) => {
            // 2-step: create then approve
            const group = await createDraftGroup({
                name: values.name || undefined,
                lines: values.lines.map(l => ({
                    article_id: parseInt(l.article_id),
                    batch_id: l.batch_id ? parseInt(l.batch_id) : null,
                    quantity_kg: l.quantity_kg,
                    note: l.note,
                    client_event_id: l.client_event_id
                }))
            });

            return approveDraftGroup(group.id);
        },
        onSuccess: () => {
            notifications.show({
                title: 'Success',
                message: 'Draft group created and approved successfully.',
                color: 'green',
                icon: <IconCheck size={16} />
            });
            form.reset();
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
            queryClient.invalidateQueries({ queryKey: ['inventory'] });
        },
        onError: (err) => {
            notifications.show({
                title: 'Approval Failed',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />
            });
        }
    });

    return (
        <Stack gap="md">
            <TextInput
                label="Group Name (Optional)"
                placeholder="e.g. Morning Batch Weigh-in"
                {...form.getInputProps('name')}
                style={{ maxWidth: 400 }}
            />

            <Table striped withTableBorder withColumnBorders>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th w={80}>Loc</Table.Th>
                        <Table.Th w={200}>Article</Table.Th>
                        <Table.Th w={200}>Description</Table.Th>
                        <Table.Th w={150}>Mfr</Table.Th>
                        <Table.Th w={80}>UOM</Table.Th>
                        <Table.Th w={200}>Batch</Table.Th>
                        <Table.Th w={120}>Qty (KG)</Table.Th>
                        <Table.Th>Note</Table.Th>
                        <Table.Th w={80}></Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                    {form.values.lines.map((_, index) => (
                        <Row
                            key={index}
                            index={index}
                            form={form}
                            articles={articlesQuery.data || []}
                        />
                    ))}
                </Table.Tbody>
            </Table>

            <Group justify="space-between">
                <Button
                    variant="light"
                    leftSection={<IconPlus size={16} />}
                    onClick={() => form.insertListItem('lines', {
                        article_id: '', batch_id: '', quantity_kg: 0, note: '', client_event_id: uuidv4()
                    })}
                >
                    Add Row
                </Button>

                <Group>
                    <Button
                        variant="default"
                        onClick={() => form.reset()}
                        disabled={createMutation.isPending || approveMutation.isPending}
                    >
                        Clear All
                    </Button>
                    <Button
                        color="blue"
                        loading={createMutation.isPending}
                        disabled={approveMutation.isPending}
                        onClick={() => form.onSubmit((v) => createMutation.mutate(v))()}
                    >
                        Save as Draft
                    </Button>
                    <Button
                        color="green"
                        rightSection={<IconArrowRight size={16} />}
                        loading={approveMutation.isPending}
                        disabled={createMutation.isPending}
                        onClick={() => form.onSubmit((v) => approveMutation.mutate(v))()}
                    >
                        Approve Now
                    </Button>
                </Group>
            </Group>
        </Stack>
    );
}

function Row({ index, form, articles }: { index: number, form: any, articles: any[] }) {
    const articleId = form.values.lines[index].article_id;
    const selectedArticle = articles.find(a => a.value === articleId);
    const isConsumable = selectedArticle && selectedArticle.is_paint === false;
    const selectRef = useRef<HTMLInputElement>(null);

    // Fetch batches for this specific row
    const batchesQuery = useQuery({
        queryKey: ['batches', selectedArticle?.article_no],
        queryFn: () => getBatchesByArticle(selectedArticle!.article_no),
        enabled: !!selectedArticle?.article_no && !isConsumable,
    });

    const batchOptions = batchesQuery.data?.items.map(b => ({
        value: b.id.toString(),
        label: `${b.batch_code} ${b.expiry_date ? `(Exp: ${dayjs(b.expiry_date).format('DD.MM.YYYY')})` : ''}`
    })) || [];

    // Auto-focus logic for new rows
    useEffect(() => {
        if (index === form.values.lines.length - 1 && !articleId) {
            // Give a small timeout to let the new row render
            setTimeout(() => selectRef.current?.focus(), 50);
        }
    }, [form.values.lines.length]);

    return (
        <Table.Tr>
            <Table.Td>
                <TextInput
                    value="13"
                    readOnly
                    variant="filled"
                    styles={{ input: { textAlign: 'center', fontWeight: 700, backgroundColor: '#f8f9fa' } }}
                />
            </Table.Td>
            <Table.Td>
                <Select
                    ref={selectRef}
                    placeholder="Search..."
                    data={articles}
                    searchable
                    nothingFoundMessage="No articles found"
                    {...form.getInputProps(`lines.${index}.article_id`)}
                    onChange={(val) => {
                        form.setFieldValue(`lines.${index}.article_id`, val || '');
                        form.setFieldValue(`lines.${index}.batch_id`, ''); // Reset batch
                    }}
                />
            </Table.Td>
            <Table.Td>
                <TextInput
                    readOnly
                    variant="filled"
                    value={selectedArticle?.description || ''}
                    styles={{ input: { fontSize: 'xs' } }}
                />
            </Table.Td>
            <Table.Td>
                <TextInput
                    readOnly
                    variant="filled"
                    value={selectedArticle?.manufacturer || ''}
                    styles={{ input: { fontSize: 'xs' } }}
                />
            </Table.Td>
            <Table.Td>
                <TextInput
                    readOnly
                    variant="filled"
                    value={selectedArticle?.uom || ''}
                    styles={{ input: { textAlign: 'center' } }}
                />
            </Table.Td>
            <Table.Td>
                {selectedArticle?.is_paint === false ? (
                    <Badge color="gray" variant="light" fullWidth>System Batch (NA)</Badge>
                ) : (
                    <Select
                        placeholder={!articleId ? "Select article" : "Select batch"}
                        data={batchOptions}
                        searchable
                        disabled={!articleId || batchesQuery.isLoading}
                        {...form.getInputProps(`lines.${index}.batch_id`)}
                    />
                )}
            </Table.Td>
            <Table.Td>
                <NumberInput
                    placeholder="0.00"
                    decimalScale={2}
                    fixedDecimalScale
                    min={0.01}
                    step={0.01}
                    {...form.getInputProps(`lines.${index}.quantity_kg`)}
                />
            </Table.Td>
            <Table.Td>
                <TextInput
                    placeholder="Note..."
                    {...form.getInputProps(`lines.${index}.note`)}
                />
            </Table.Td>
            <Table.Td>
                <Group gap={4} wrap="nowrap">
                    <Tooltip label="Duplicate Row">
                        <ActionIcon
                            variant="subtle"
                            color="blue"
                            onClick={() => {
                                const current = form.values.lines[index];
                                form.insertListItem('lines', {
                                    ...current,
                                    client_event_id: uuidv4()
                                });
                            }}
                        >
                            <IconCopy size={16} />
                        </ActionIcon>
                    </Tooltip>
                    <ActionIcon
                        variant="subtle"
                        color="red"
                        onClick={() => form.removeListItem('lines', index)}
                        disabled={form.values.lines.length === 1}
                    >
                        <IconTrash size={16} />
                    </ActionIcon>
                </Group>
            </Table.Td>
        </Table.Tr>
    );
}
