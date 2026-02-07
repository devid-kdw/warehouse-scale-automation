import { Container, Title, Accordion, Table, Group, Text, Badge, LoadingOverlay, Paper, Stack } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { getReceiptHistory, extractErrorMessage } from '../../api/services';
import { IconHistory, IconAlertCircle } from '@tabler/icons-react';
import { EmptyState } from '../../components/common/EmptyState';
import dayjs from 'dayjs';

export default function ReceiptHistory() {
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['receiptHistory'],
        queryFn: getReceiptHistory,
    });

    const items = data?.history.map((group) => (
        <Accordion.Item key={group.receipt_key} value={group.receipt_key}>
            <Accordion.Control>
                <Group justify="space-between" pr="md">
                    <Stack gap={0}>
                        <Text fw={700}>Order: {group.order_number}</Text>
                        <Text size="xs" c="dimmed">Key: {group.receipt_key}</Text>
                    </Stack>
                    <Group>
                        <Badge variant="light" color="blue">
                            {group.lines.length} {group.lines.length === 1 ? 'item' : 'items'}
                        </Badge>
                        <Text size="sm" c="dimmed">
                            {dayjs(group.received_at).format('DD.MM.YYYY HH:mm')}
                        </Text>
                    </Group>
                </Group>
            </Accordion.Control>
            <Accordion.Panel>
                <Table striped highlightOnHover verticalSpacing="xs">
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>Article</Table.Th>
                            <Table.Th>Description</Table.Th>
                            <Table.Th>Batch</Table.Th>
                            <Table.Th align="right">Qty (kg)</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {group.lines.map((line, idx) => (
                            <Table.Tr key={`${group.receipt_key}-${idx}`}>
                                <Table.Td>{line.article_no}</Table.Td>
                                <Table.Td>{line.description}</Table.Td>
                                <Table.Td>
                                    <Badge variant="dot" color={line.batch_code === 'NA' ? 'gray' : 'blue'}>
                                        {line.batch_code}
                                    </Badge>
                                </Table.Td>
                                <Table.Td fw={700} align="right">{line.quantity_kg.toFixed(2)}</Table.Td>
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            </Accordion.Panel>
        </Accordion.Item>
    ));

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>
                    <Group>
                        <IconHistory size={28} />
                        Receipt History
                    </Group>
                </Title>
            </Group>

            <Paper shadow="xs" p="md" withBorder style={{ position: 'relative' }}>
                <LoadingOverlay visible={isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

                {isError && (
                    <Text c="red" mt="md">
                        <Group>
                            <IconAlertCircle size={16} />
                            Error: {extractErrorMessage(error)}
                        </Group>
                    </Text>
                )}

                {(!data || data.history.length === 0) && !isLoading && (
                    <EmptyState message="No receipt history found." />
                )}

                {data && data.history.length > 0 && (
                    <Accordion variant="separated">
                        {items}
                    </Accordion>
                )}
            </Paper>
        </Container>
    );
}
