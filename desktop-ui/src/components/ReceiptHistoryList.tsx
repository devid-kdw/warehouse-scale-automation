import { Accordion, Table, Group, Text, Badge, LoadingOverlay, Paper, Stack } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { getReceiptHistory, extractErrorMessage } from '../api/services';
import { IconAlertCircle } from '@tabler/icons-react';
import { EmptyState } from './common/EmptyState';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

export function ReceiptHistoryList() {
    const { t } = useTranslation('common');
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['receiptHistory'],
        queryFn: getReceiptHistory,
    });

    const items = data?.history.map((group) => (
        <Accordion.Item key={group.receipt_key} value={group.receipt_key}>
            <Accordion.Control>
                <Group justify="space-between" pr="md">
                    <Stack gap={0}>
                        <Text fw={700}>{t('receiving.deliveryNote')}: {group.delivery_note_number || '-'}</Text>
                        <Text size="xs" c="dimmed">{t('receiving.receiptNumber')}: {group.receipt_key}</Text>
                    </Stack>
                    <Group>
                        <Badge variant="light" color="blue">
                            {group.lines.length} {group.lines.length === 1 ? 'stavka' : group.lines.length < 5 ? 'stavke' : 'stavki'}
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
                            <Table.Th>{t('nav.articles')}</Table.Th>
                            <Table.Th>Naziv</Table.Th>
                            <Table.Th>{t('receiving.batchCode')}</Table.Th>
                            <Table.Th>Primio</Table.Th>
                            <Table.Th ta="right">{t('receiving.quantity')}</Table.Th>
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
                                <Table.Td>{line.user_name || '-'}</Table.Td>
                                <Table.Td fw={700} ta="right">{line.quantity.toFixed(2)} {line.uom}</Table.Td>
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            </Accordion.Panel>
        </Accordion.Item>
    ));

    return (
        <Paper shadow="xs" p="md" withBorder style={{ position: 'relative' }}>
            <LoadingOverlay visible={isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

            {isError && (
                <Text c="red" mt="md">
                    <Group>
                        <IconAlertCircle size={16} />
                        {t('common.error')}: {extractErrorMessage(error)}
                    </Group>
                </Text>
            )}

            {(!data || data.history.length === 0) && !isLoading && (
                <EmptyState message="Nema nedavnih primki." />
            )}

            {data && data.history.length > 0 && (
                <Accordion variant="separated">
                    {items}
                </Accordion>
            )}
        </Paper>
    );
}
