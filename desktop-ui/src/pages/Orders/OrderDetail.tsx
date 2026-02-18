import { Container, Title, Paper, Stack, Group, Button, TextInput, Table, Badge, ActionIcon } from '@mantine/core';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { IconArrowLeft, IconEdit, IconTrash } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { getOrder, updateOrder, removeOrderLine, OrderUpdatePayload } from '../../api/orders';

export default function OrderDetail() {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();
    const queryClient = useQueryClient();
    const [editMode, setEditMode] = useState(false);
    const [editedHeader, setEditedHeader] = useState({ supplier_code: '', supplier_name: '', note: '' });

    const { data: order, isLoading, error } = useQuery({
        queryKey: ['orders', id],
        queryFn: () => getOrder(Number(id)),
        enabled: !!id,
    });

    const updateMutation = useMutation({
        mutationFn: (data: OrderUpdatePayload) => updateOrder(Number(id), data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders', id] });
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            notifications.show({
                title: t('common.success'),
                message: 'Narudžba uspješno ažurirana',
                color: 'green',
            });
            setEditMode(false);
        },
        onError: (error: Error) => {
            notifications.show({
                title: t('common.error'),
                message: error.message,
                color: 'red',
            });
        },
    });

    const removeLineMutation = useMutation({
        mutationFn: ({ orderId, lineId }: { orderId: number; lineId: number }) =>
            removeOrderLine(orderId, lineId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders', id] });
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            notifications.show({
                title: t('common.success'),
                message: 'Stavka uspješno uklonjena',
                color: 'green',
            });
        },
        onError: (error: Error) => {
            notifications.show({
                title: t('common.error'),
                message: error.message,
                color: 'red',
            });
        },
    });

    if (isLoading) {
        return (
            <Container>
                <Title order={2}>{t('common.loading')}</Title>
            </Container>
        );
    }

    if (error || !order) {
        return (
            <Container>
                <Title order={2} c="red">{t('common.error')}</Title>
                <p>{(error as Error)?.message || 'Narudžba nije pronađena'}</p>
            </Container>
        );
    }

    // Filter out removed lines
    const activeLines = order.lines.filter(l => l.status !== 'REMOVED');

    const handleSaveHeader = () => {
        updateMutation.mutate({
            supplier_code: editedHeader.supplier_code || undefined,
            supplier_name: editedHeader.supplier_name || undefined,
            note: editedHeader.note || undefined,
        });
    };

    const handleEditClick = () => {
        setEditedHeader({
            supplier_code: order.supplier_code || '',
            supplier_name: order.supplier_name || '',
            note: order.note || '',
        });
        setEditMode(true);
    };

    const handleRemoveLine = (lineId: number) => {
        if (confirm(t('orders.removeLine') + '?')) {
            removeLineMutation.mutate({ orderId: order.id, lineId });
        }
    };

    return (
        <Container size="xl" className="page-container">
            <Stack gap="md">
                <Group justify="space-between">
                    <Group>
                        <ActionIcon onClick={() => navigate('/orders/open')} variant="subtle">
                            <IconArrowLeft size={20} />
                        </ActionIcon>
                        <Title order={2}>{order.order_number}</Title>
                        <Badge color={order.status === 'OPEN' ? 'blue' : 'green'}>
                            {order.status === 'OPEN' ? t('orders.open') : t('orders.closed')}
                        </Badge>
                    </Group>
                    {!editMode && order.status === 'OPEN' && (
                        <Button
                            leftSection={<IconEdit size={16} />}
                            onClick={handleEditClick}
                        >
                            {t('orders.editOrder')}
                        </Button>
                    )}
                </Group>

                <Paper p="md" withBorder>
                    <Stack gap="sm">
                        <Title order={4}>{t('orders.title')}</Title>
                        {editMode ? (
                            <>
                                <TextInput
                                    label={t('orders.supplierCode')}
                                    value={editedHeader.supplier_code}
                                    onChange={(e) => setEditedHeader({ ...editedHeader, supplier_code: e.currentTarget.value })}
                                />
                                <TextInput
                                    label={t('orders.supplierName')}
                                    value={editedHeader.supplier_name}
                                    onChange={(e) => setEditedHeader({ ...editedHeader, supplier_name: e.currentTarget.value })}
                                />
                                <TextInput
                                    label="Napomena"
                                    value={editedHeader.note}
                                    onChange={(e) => setEditedHeader({ ...editedHeader, note: e.currentTarget.value })}
                                />
                                <Group>
                                    <Button onClick={handleSaveHeader}>{t('common.save')}</Button>
                                    <Button variant="subtle" onClick={() => setEditMode(false)}>
                                        {t('common.cancel')}
                                    </Button>
                                </Group>
                            </>
                        ) : (
                            <>
                                <Group>
                                    <strong>{t('orders.supplierCode')}:</strong> {order.supplier_code || '-'}
                                </Group>
                                <Group>
                                    <strong>{t('orders.supplierName')}:</strong> {order.supplier_name || '-'}
                                </Group>
                                {order.note && (
                                    <Group>
                                        <strong>Napomena:</strong> {order.note}
                                    </Group>
                                )}
                            </>
                        )}
                    </Stack>
                </Paper>

                <Paper p="md" withBorder>
                    <Stack gap="sm">
                        <Group justify="space-between">
                            <Title order={4}>{t('orders.lines')} ({activeLines.length})</Title>
                        </Group>

                        <Table striped>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Artikl</Table.Th>
                                    <Table.Th>{t('orders.orderedQty')}</Table.Th>
                                    <Table.Th>{t('orders.receivedQty')}</Table.Th>
                                    <Table.Th>{t('receiving.uom')}</Table.Th>
                                    <Table.Th>{t('orders.deliveryDate')}</Table.Th>
                                    <Table.Th>{t('orders.status')}</Table.Th>
                                    {order.status === 'OPEN' && <Table.Th>Akcije</Table.Th>}
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {activeLines.map((line) => (
                                    <Table.Tr key={line.id}>
                                        <Table.Td>{line.article_no}</Table.Td>
                                        <Table.Td>{line.ordered_qty}</Table.Td>
                                        <Table.Td>{line.received_qty}</Table.Td>
                                        <Table.Td>{line.uom}</Table.Td>
                                        <Table.Td>{line.delivery_date || '-'}</Table.Td>
                                        <Table.Td>
                                            {line.status === 'CLOSED' ? (
                                                <Badge color="green">Ispunjeno</Badge>
                                            ) : (
                                                <Badge color="yellow">Na čekanju</Badge>
                                            )}
                                        </Table.Td>
                                        {order.status === 'OPEN' && (
                                            <Table.Td>
                                                <ActionIcon
                                                    color="red"
                                                    onClick={() => handleRemoveLine(line.id)}
                                                >
                                                    <IconTrash size={16} />
                                                </ActionIcon>
                                            </Table.Td>
                                        )}
                                    </Table.Tr>
                                ))}
                                {activeLines.length === 0 && (
                                    <Table.Tr>
                                        <Table.Td colSpan={7} style={{ textAlign: 'center' }}>
                                            Nema aktivnih stavki
                                        </Table.Td>
                                    </Table.Tr>
                                )}
                            </Table.Tbody>
                        </Table>
                    </Stack>
                </Paper>
            </Stack>
        </Container>
    );
}
