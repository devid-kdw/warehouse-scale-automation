import { Container, Title, Table, Badge, TextInput, Stack } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { IconSearch } from '@tabler/icons-react';
import { listOrders, Order } from '../../api/orders';

export default function ClosedOrders() {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');

    const { data, isLoading, error } = useQuery({
        queryKey: ['orders', 'CLOSED'],
        queryFn: () => listOrders('CLOSED'),
    });

    const filteredOrders = data?.items.filter(order => {
        const query = searchQuery.toLowerCase();
        return (
            order.order_number.toLowerCase().includes(query) ||
            order.supplier_name?.toLowerCase().includes(query) ||
            order.supplier_code?.toLowerCase().includes(query)
        );
    }) || [];

    if (error) {
        return (
            <Container>
                <Title order={2} c="red">{t('common.error')}</Title>
                <p>{(error as Error).message}</p>
            </Container>
        );
    }

    return (
        <Container size="xl" className="page-container">
            <Stack gap="md">
                <Title order={2}>{t('nav.closedOrders')}</Title>

                <TextInput
                    placeholder={t('common.search')}
                    leftSection={<IconSearch size={16} />}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.currentTarget.value)}
                />

                <Table striped highlightOnHover>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>{t('orders.orderNumber')}</Table.Th>
                            <Table.Th>{t('orders.supplierName')}</Table.Th>
                            <Table.Th>{t('orders.supplierCode')}</Table.Th>
                            <Table.Th>{t('orders.lines')}</Table.Th>
                            <Table.Th>{t('orders.status')}</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {isLoading && (
                            <Table.Tr>
                                <Table.Td colSpan={5} style={{ textAlign: 'center' }}>
                                    {t('common.loading')}
                                </Table.Td>
                            </Table.Tr>
                        )}
                        {!isLoading && filteredOrders.length === 0 && (
                            <Table.Tr>
                                <Table.Td colSpan={5} style={{ textAlign: 'center' }}>
                                    No closed orders
                                </Table.Td>
                            </Table.Tr>
                        )}
                        {filteredOrders.map((order: Order) => (
                            <Table.Tr
                                key={order.id}
                                style={{ cursor: 'pointer' }}
                                onClick={() => navigate(`/orders/${order.id}`)}
                            >
                                <Table.Td>{order.order_number}</Table.Td>
                                <Table.Td>{order.supplier_name || '-'}</Table.Td>
                                <Table.Td>{order.supplier_code || '-'}</Table.Td>
                                <Table.Td>{order.lines.filter(l => l.status !== 'REMOVED').length}</Table.Td>
                                <Table.Td>
                                    <Badge color="green">{t('orders.closed')}</Badge>
                                </Table.Td>
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            </Stack>
        </Container>
    );
}
