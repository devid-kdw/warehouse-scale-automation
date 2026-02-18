import { Container, Title, Paper, Stack, Group, Button, TextInput, Radio, NumberInput, Select, Table, ActionIcon, Text, Divider, Alert } from '@mantine/core';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useForm } from '@mantine/form';
import { useNavigate } from 'react-router-dom';
import { IconArrowLeft, IconCheck, IconPlus, IconTrash, IconAlertTriangle } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { createOrder, OrderCreatePayload } from '../../api/orders';
import { getArticles } from '../../api/services';
import { useState } from 'react';

interface LineItem {
    article_id: number;
    article_no: string;
    ordered_qty: number;
    uom: string;
    delivery_date: string;
    note: string;
}

export default function CreateOrder() {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [lines, setLines] = useState<LineItem[]>([]);
    const [lineError, setLineError] = useState<string | null>(null);

    // Fetch articles for line selection
    const { data: articlesData } = useQuery({
        queryKey: ['articles', 'all'],
        queryFn: () => getArticles('all'),
    });
    const articles = articlesData?.items || [];

    // Line form state
    const lineForm = useForm({
        initialValues: {
            article_id: '',
            ordered_qty: 1,
            uom: 'KG',
            delivery_date: '',
            note: '',
        },
        validate: {
            article_id: (v) => !v ? 'Artikl je obavezan' : null,
            ordered_qty: (v) => v <= 0 ? 'Količina mora biti > 0' : null,
            uom: (v) => !v ? 'JM je obavezna' : null,
        },
    });

    const form = useForm({
        initialValues: {
            numberType: 'auto',
            order_number: '',
            supplier_code: '',
            supplier_name: '',
            note: '',
        },
        validate: {
            order_number: (value, values) =>
                values.numberType === 'manual' && !value ? 'Broj narudžbe je obavezan' : null,
        },
    });

    const createMutation = useMutation({
        mutationFn: (data: OrderCreatePayload) => createOrder(data),
        onSuccess: (order) => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            notifications.show({
                title: t('common.success'),
                message: 'Narudžba uspješno kreirana',
                color: 'green',
            });
            navigate(`/orders/${order.id}`);
        },
        onError: (error: Error) => {
            notifications.show({
                title: t('common.error'),
                message: error.message,
                color: 'red',
            });
        },
    });

    const handleAddLine = lineForm.onSubmit((values) => {
        const article = articles.find(a => a.id === Number(values.article_id));
        if (!article) return;
        setLines(prev => [...prev, {
            article_id: Number(values.article_id),
            article_no: article.article_no,
            ordered_qty: values.ordered_qty,
            uom: values.uom,
            delivery_date: values.delivery_date,
            note: values.note,
        }]);
        lineForm.reset();
        lineForm.setFieldValue('uom', 'KG');
        lineForm.setFieldValue('ordered_qty', 1);
        setLineError(null);
    });

    const handleRemoveLine = (index: number) => {
        setLines(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = form.onSubmit((values) => {
        // T08 fix: validate min 1 line before submit
        if (lines.length === 0) {
            setLineError('Dodajte barem jednu stavku narudžbe prije slanja.');
            return;
        }
        setLineError(null);
        createMutation.mutate({
            order_number: values.numberType === 'auto' ? 'auto' : values.order_number,
            supplier_code: values.supplier_code || undefined,
            supplier_name: values.supplier_name || undefined,
            note: values.note || undefined,
            lines: lines.map(l => ({
                article_id: l.article_id,
                ordered_qty: l.ordered_qty,
                uom: l.uom,
                delivery_date: l.delivery_date || undefined,
                note: l.note || undefined,
            })),
        });
    });

    return (
        <Container size="lg" className="page-container">
            <Stack gap="md">
                <Group>
                    <Button variant="subtle" leftSection={<IconArrowLeft size={16} />} onClick={() => navigate('/orders/open')}>
                        {t('common.cancel')}
                    </Button>
                    <Title order={2}>{t('orders.createOrder')}</Title>
                </Group>

                <form onSubmit={handleSubmit}>
                    <Stack gap="md">
                        {/* Order Header */}
                        <Paper p="lg" withBorder>
                            <Title order={4} mb="md">Zaglavlje narudžbe</Title>
                            <Stack gap="sm">
                                <Radio.Group
                                    label={t('orders.orderNumber')}
                                    {...form.getInputProps('numberType')}
                                >
                                    <Group mt="xs">
                                        <Radio value="auto" label={t('orders.autoNumber')} />
                                        <Radio value="manual" label="Ručni unos" />
                                    </Group>
                                </Radio.Group>

                                {form.values.numberType === 'manual' && (
                                    <TextInput
                                        label="Prilagođeni broj narudžbe"
                                        placeholder="ORD-..."
                                        required
                                        {...form.getInputProps('order_number')}
                                    />
                                )}

                                <TextInput
                                    label={t('orders.supplierCode')}
                                    {...form.getInputProps('supplier_code')}
                                />
                                <TextInput
                                    label={t('orders.supplierName')}
                                    {...form.getInputProps('supplier_name')}
                                />
                                <TextInput
                                    label="Napomena"
                                    {...form.getInputProps('note')}
                                />
                            </Stack>
                        </Paper>

                        {/* Line Items */}
                        <Paper p="lg" withBorder>
                            <Title order={4} mb="md">{t('orders.lines')} ({lines.length})</Title>

                            {lineError && (
                                <Alert icon={<IconAlertTriangle size={16} />} color="red" mb="md">
                                    {lineError}
                                </Alert>
                            )}

                            {/* Existing lines table */}
                            {lines.length > 0 && (
                                <Table striped mb="md">
                                    <Table.Thead>
                                        <Table.Tr>
                                            <Table.Th>Artikl</Table.Th>
                                            <Table.Th>Kol.</Table.Th>
                                            <Table.Th>JM</Table.Th>
                                            <Table.Th>{t('orders.deliveryDate')}</Table.Th>
                                            <Table.Th>Napomena</Table.Th>
                                            <Table.Th w={40}></Table.Th>
                                        </Table.Tr>
                                    </Table.Thead>
                                    <Table.Tbody>
                                        {lines.map((line, i) => (
                                            <Table.Tr key={i}>
                                                <Table.Td>{line.article_no}</Table.Td>
                                                <Table.Td>{line.ordered_qty}</Table.Td>
                                                <Table.Td>{line.uom}</Table.Td>
                                                <Table.Td>{line.delivery_date || '-'}</Table.Td>
                                                <Table.Td>{line.note || '-'}</Table.Td>
                                                <Table.Td>
                                                    <ActionIcon color="red" variant="subtle" onClick={() => handleRemoveLine(i)}>
                                                        <IconTrash size={14} />
                                                    </ActionIcon>
                                                </Table.Td>
                                            </Table.Tr>
                                        ))}
                                    </Table.Tbody>
                                </Table>
                            )}

                            {/* Add line form */}
                            <Divider label="Dodaj stavku" labelPosition="left" mb="sm" />
                            <Stack gap="sm">
                                <Group align="flex-end" grow>
                                    <Select
                                        label="Artikl"
                                        placeholder="Odaberi artikl..."
                                        searchable
                                        data={articles.map(a => ({ value: a.id.toString(), label: `${a.article_no} — ${a.description}` }))}
                                        {...lineForm.getInputProps('article_id')}
                                    />
                                    <NumberInput
                                        label="Količina"
                                        min={0.01}
                                        decimalScale={2}
                                        {...lineForm.getInputProps('ordered_qty')}
                                    />
                                    <Select
                                        label="JM"
                                        data={['KG', 'L', 'KOM', 'M', 'M2']}
                                        {...lineForm.getInputProps('uom')}
                                    />
                                </Group>
                                <Group align="flex-end" grow>
                                    <TextInput
                                        label={t('orders.deliveryDate')}
                                        placeholder="YYYY-MM-DD"
                                        {...lineForm.getInputProps('delivery_date')}
                                    />
                                    <TextInput
                                        label="Napomena stavke"
                                        {...lineForm.getInputProps('note')}
                                    />
                                    <Button
                                        leftSection={<IconPlus size={16} />}
                                        variant="light"
                                        onClick={() => handleAddLine()}
                                        style={{ alignSelf: 'flex-end' }}
                                    >
                                        {t('orders.addLine')}
                                    </Button>
                                </Group>
                            </Stack>
                        </Paper>

                        {/* Submit */}
                        <Group justify="flex-end">
                            <Text size="sm" c="dimmed">
                                {lines.length === 0 ? 'Dodajte barem jednu stavku' : `${lines.length} stavka/e`}
                            </Text>
                            <Button
                                type="submit"
                                loading={createMutation.isPending}
                                leftSection={<IconCheck size={16} />}
                                disabled={lines.length === 0}
                            >
                                {t('orders.createOrder')}
                            </Button>
                        </Group>
                    </Stack>
                </form>
            </Stack>
        </Container>
    );
}
