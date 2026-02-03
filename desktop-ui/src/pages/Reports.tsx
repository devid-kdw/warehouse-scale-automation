import { useState } from 'react';
import {
    Container, Title, Paper, Table, Group, Button, TextInput,
    Badge, LoadingOverlay, Text, Box, Select
} from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { useQuery } from '@tanstack/react-query';
import { IconSearch, IconFileSpreadsheet } from '@tabler/icons-react';
import { getTransactions, extractErrorMessage } from '../api/services';
import { Transaction } from '../api/types';
import { EmptyState } from '../components/common/EmptyState';
import dayjs from 'dayjs';

export default function Reports() {
    const [page] = useState(1);
    const [search, setSearch] = useState('');
    const [typeFilter, setTypeFilter] = useState<string | null>(null);
    const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['transactions', page, search, typeFilter, dateRange],
        queryFn: () => getTransactions({
            page,
            search,
            type: typeFilter,
            start_date: dateRange[0] ? dayjs(dateRange[0]).format('YYYY-MM-DD') : undefined,
            end_date: dateRange[1] ? dayjs(dateRange[1]).format('YYYY-MM-DD') : undefined,
        }),
    });

    const rows = data?.items.map((tx: Transaction) => (
        <Table.Tr key={tx.id}>
            <Table.Td>{tx.id}</Table.Td>
            <Table.Td>{dayjs(tx.occurred_at).format('DD.MM.YYYY HH:mm')}</Table.Td>
            <Table.Td>
                <Badge
                    color={
                        tx.tx_type === 'WEIGH_IN' ? 'green' :
                            tx.tx_type === 'CONSUMPTION' ? 'blue' :
                                'gray'
                    }
                >
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
                    <TextInput
                        label="Search"
                        placeholder="Article, Batch, User..."
                        leftSection={<IconSearch size={16} />}
                        value={search}
                        onChange={(e) => setSearch(e.currentTarget.value)}
                        style={{ flex: 1 }}
                    />
                    <Select
                        label="Type"
                        placeholder="All Types"
                        data={['WEIGH_IN', 'CONSUMPTION', 'ADJUSTMENT']}
                        value={typeFilter}
                        onChange={setTypeFilter}
                        clearable
                        style={{ width: 200 }}
                    />
                    <DatePickerInput
                        type="range"
                        label="Date Range"
                        placeholder="Pick dates"
                        value={dateRange}
                        onChange={setDateRange}
                        style={{ width: 250 }}
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
