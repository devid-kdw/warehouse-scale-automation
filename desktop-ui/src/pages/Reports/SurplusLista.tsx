
import { Table, Button, Group, Title, LoadingOverlay, Alert, Text } from '@mantine/core';
import { useMutation, useQuery } from '@tanstack/react-query';
import { IconDownload, IconAlertCircle } from '@tabler/icons-react';
import { getSurplusLista, downloadReportExport, extractErrorMessage } from '../../api/services';
import { notifications } from '@mantine/notifications';
import { EmptyState } from '../../components/common/EmptyState';

// P1 fix: SurplusItemSchema fields: article_no, description, batch_code, quantity, uom, updated_at
interface SurplusItem {
    article_no: string;
    description?: string;
    batch_code: string;
    quantity: number;  // P1 fix: was 'quantity_kg', backend canonical field is 'quantity'
    uom: string;
    updated_at?: string;
}

export function SurplusLista() {
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['report', 'surplus'],
        queryFn: getSurplusLista
    });

    // P1 fix: auth-safe export using apiClient blob download
    const exportMutation = useMutation({
        mutationFn: (format: 'excel' | 'pdf') => downloadReportExport('surplus', format),
        onSuccess: () => {
            notifications.show({ title: 'Preuzimanje', message: 'Izvještaj je preuzet.', color: 'green' });
        },
        onError: (err) => {
            notifications.show({ title: 'Greška', message: extractErrorMessage(err), color: 'red', icon: <IconAlertCircle size={16} /> });
        }
    });

    // P1 fix: backend returns {items: SurplusItemSchema[], total: N}
    const items: SurplusItem[] = data?.items || [];

    const rows = items.map((item, index) => (
        <Table.Tr key={`${item.article_no}-${item.batch_code}-${index}`}>
            <Table.Td fw={700}>{item.article_no}</Table.Td>
            <Table.Td>{item.description || '-'}</Table.Td>
            <Table.Td>{item.batch_code}</Table.Td>
            {/* P1 fix: field is 'quantity' not 'surplus_qty' */}
            <Table.Td ta="right" fw={700} c="green">{item.quantity?.toFixed(2) ?? '-'}</Table.Td>
            <Table.Td>{item.uom || '-'}</Table.Td>
        </Table.Tr>
    ));

    return (
        <div>
            <Group justify="space-between" mb="md">
                <Title order={3}>Viškovi</Title>
                <Group>
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
                    <EmptyState message="Nema viškova." />
                ) : (
                    <Table striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Šifra artikla</Table.Th>
                                <Table.Th>Naziv</Table.Th>
                                <Table.Th>Šarža</Table.Th>
                                <Table.Th ta="right">Višak (kol.)</Table.Th>
                                <Table.Th>JM</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {rows}
                            {items.length > 0 && (
                                <Table.Tr>
                                    <Table.Td colSpan={5}>
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
