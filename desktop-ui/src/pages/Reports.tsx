import { useState } from 'react';
import {
    Container, Title, Paper, Table, Group, Button,
    Badge, LoadingOverlay, Text, Box, Select
} from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { useQuery } from '@tanstack/react-query';
import { IconFileSpreadsheet } from '@tabler/icons-react';
import { getTransactions, extractErrorMessage } from '../api/services';
import { Transaction } from '../api/types';
import { EmptyState } from '../components/common/EmptyState';
import dayjs from 'dayjs';

const TX_TYPE_OPTIONS = [
    { value: 'WEIGH_IN', label: 'Weigh-In' },
    { value: 'SURPLUS_CONSUMED', label: 'Surplus Consumed' },
    { value: 'STOCK_CONSUMED', label: 'Stock Consumed' },
    { value: 'INVENTORY_ADJUSTMENT', label: 'Inventory Adjustment' },
];

const TX_TYPE_COLORS: Record<string, string> = {
    'WEIGH_IN': 'green',
    'SURPLUS_CONSUMED': 'orange',
    'STOCK_CONSUMED': 'blue',
    'INVENTORY_ADJUSTMENT': 'violet',
    'STOCK_RECEIPT': 'teal',
};

export default function Reports() {
    const [txType, setTxType] = useState<string | null>(null);
    const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['transactions', txType, dateRange],
        queryFn: () => getTransactions({
            tx_type: txType || undefined,
            from: dateRange[0] ? dayjs(dateRange[0]).startOf('day').toISOString() : undefined,
            to: dateRange[1] ? dayjs(dateRange[1]).endOf('day').toISOString() : undefined,
            limit: 200,
            offset: 0,
        }),
    });

    const rows = data?.items.map((tx: Transaction) => (
        <Table.Tr key={tx.id}>
            <Table.Td>{tx.id}</Table.Td>
            <Table.Td>{dayjs(tx.occurred_at).format('DD.MM.YYYY HH:mm')}</Table.Td>
            <Table.Td>
                <Badge color={TX_TYPE_COLORS[tx.tx_type] || 'gray'}>
                    {tx.tx_type}
                </Badge>
            </Table.Td>
            <Table.Td>{tx.article_no}</Table.Td>
            <Table.Td>{tx.batch_code}</Table.Td>
            <Table.Td>{tx.location_code}</Table.Td>
            <Table.Td fw={700} c={tx.quantity_kg > 0 ? 'green' : 'red'}>
                {tx.quantity_kg > 0 ? '+' : ''}{tx.quantity_kg.toFixed(2)} KG
            </Table.Td>
            <Table.Td>{tx.source}</Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Transaction Reports</Title>
                <Button leftSection={<IconFileSpreadsheet size={16} />} variant="outline">
                    Export CSV
                </Button>
            </Group>

            <Paper shadow="xs" p="md" withBorder mb="lg">
                <Group align="flex-end">
                    <Select
                        label="Transaction Type"
                        placeholder="All Types"
                        data={TX_TYPE_OPTIONS}
                        value={txType}
                        onChange={setTxType}
                        clearable
                        style={{ width: 220 }}
                    />
                    <DatePickerInput
                        type="range"
                        label="Date Range"
                        placeholder="Pick dates"
                        value={dateRange}
                        onChange={setDateRange}
                        clearable
                        style={{ width: 280 }}
                    />
                </Group>
            </Paper>

            <Paper shadow="xs" p="md" withBorder pos="relative" mih={300}>
                <LoadingOverlay visible={isLoading} />

                {isError ? (
                    <Box p="lg" ta="center" c="red">
                        <Text fw={700}>Error loading transactions</Text>
                        <Text size="sm">{extractErrorMessage(error)}</Text>
                    </Box>
                ) : data?.items.length === 0 ? (
                    <EmptyState message="No transactions found matching your criteria" />
                ) : (
                    <Table striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Date & Time</Table.Th>
                                <Table.Th>Type</Table.Th>
                                <Table.Th>Article</Table.Th>
                                <Table.Th>Batch</Table.Th>
                                <Table.Th>Location</Table.Th>
                                <Table.Th>Quantity</Table.Th>
                                <Table.Th>Source</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>
        </Container>
    );
}
