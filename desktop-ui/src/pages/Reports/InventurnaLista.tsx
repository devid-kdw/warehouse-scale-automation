
import { Table, Button, Group, Title, LoadingOverlay, Alert, Text } from '@mantine/core';
import { useMutation, useQuery } from '@tanstack/react-query';
import { IconDownload, IconAlertCircle } from '@tabler/icons-react';
import { getInventurnaLista, downloadReportExport, extractErrorMessage } from '../../api/services';
import { notifications } from '@mantine/notifications';
import { EmptyState } from '../../components/common/EmptyState';

// P1 fix: InventurnaItemSchema fields: article_no, description, batch_code, stock, surplus, total, uom
interface InventurnaItem {
    article_id?: number;
    article_no: string;
    description?: string;
    batch_id?: number;
    batch_code: string;
    stock: number;
    surplus: number;
    total: number;
    uom: string;
}

export function InventurnaLista() {
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['report', 'inventurna'],
        queryFn: getInventurnaLista
    });

    // P1 fix: auth-safe export using apiClient blob download
    const exportMutation = useMutation({
        mutationFn: (format: 'excel' | 'pdf') => downloadReportExport('inventurna', format),
        onSuccess: () => {
            notifications.show({ title: 'Preuzimanje', message: 'Izvještaj je preuzet.', color: 'green' });
        },
        onError: (err) => {
            notifications.show({ title: 'Greška', message: extractErrorMessage(err), color: 'red', icon: <IconAlertCircle size={16} /> });
        }
    });

    // P1 fix: backend returns {items: InventurnaItemSchema[], total: N}
    const items: InventurnaItem[] = data?.items || [];

    const rows = items.map((item, index) => (
        <Table.Tr key={`${item.article_no}-${item.batch_code}-${index}`}>
            <Table.Td fw={700}>{item.article_no}</Table.Td>
            <Table.Td>{item.description || '-'}</Table.Td>
            <Table.Td>{item.batch_code}</Table.Td>
            {/* P1 fix: backend field is 'total' not 'total_qty' */}
            <Table.Td ta="right">{item.total?.toFixed(2) ?? '-'}</Table.Td>
            <Table.Td>{item.uom || '-'}</Table.Td>
            <Table.Td style={{ border: '1px solid #eee', width: 100 }}></Table.Td>
        </Table.Tr>
    ));

    return (
        <div>
            <Group justify="space-between" mb="md">
                <Title order={3}>Inventurna lista</Title>
                <Group>
                    <Button
                        leftSection={<IconDownload size={16} />}
                        variant="outline"
                        loading={exportMutation.isPending}
                        onClick={() => exportMutation.mutate('pdf')}
                    >
                        PDF
                    </Button>
                    <Button
                        leftSection={<IconDownload size={16} />}
                        variant="outline"
                        loading={exportMutation.isPending}
                        onClick={() => exportMutation.mutate('excel')}
                    >
                        Excel
                    </Button>
                </Group>
            </Group>

            {isError && (
                <Alert color="red" icon={<IconAlertCircle size={16} />} mb="md">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            <div style={{ position: 'relative', minHeight: 200 }}>
                <LoadingOverlay visible={isLoading} />
                {items.length === 0 && !isLoading ? (
                    <EmptyState message="Nema stavki inventure." />
                ) : (
                    <Table striped withTableBorder withColumnBorders>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Šifra artikla</Table.Th>
                                <Table.Th>Naziv</Table.Th>
                                <Table.Th>Šarža</Table.Th>
                                <Table.Th ta="right">Očekivano</Table.Th>
                                <Table.Th>JM</Table.Th>
                                <Table.Th>Prebrojano</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {rows}
                            {items.length > 0 && (
                                <Table.Tr>
                                    <Table.Td colSpan={6}>
                                        <Text size="xs" c="dimmed" ta="right">
                                            Ukupno: {items.length} stavki
                                        </Text>
                                    </Table.Td>
                                </Table.Tr>
                            )}
                        </Table.Tbody>
                    </Table>
                )}
            </div>
        </div>
    );
}
