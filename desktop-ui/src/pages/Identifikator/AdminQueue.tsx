
import { useState } from 'react';
import { Container, Title, Table, Button, Group, Badge, Modal, Select, Textarea, LoadingOverlay, Stack, Text } from '@mantine/core';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconCheck, IconX } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { getIdentifierQueue, resolveMissingReport, extractErrorMessage, getArticles } from '../../api/services';
import { MissingItemReport, AdminReportUpdatePayload } from '../../api/types';
import dayjs from 'dayjs';

// P0 fix: status values match backend AdminReportUpdateSchema
const STATUS_COLORS: Record<string, string> = {
    OPEN: 'orange',
    PENDING: 'yellow',
    IN_REVIEW: 'blue',
    RESOLVED: 'green',
    CLOSED: 'gray',
    REJECTED: 'red',
};

export function IdentifikatorAdminQueue() {
    const queryClient = useQueryClient();
    const [resolveModalOpen, setResolveModalOpen] = useState(false);
    const [selectedReport, setSelectedReport] = useState<MissingItemReport | null>(null);
    // P0 fix: action maps to backend status values
    const [newStatus, setNewStatus] = useState<AdminReportUpdatePayload['status']>('RESOLVED');
    const [resolvedArticleId, setResolvedArticleId] = useState<string | null>(null);
    const [adminNote, setAdminNote] = useState('');

    // Fetch Queue
    const { data: reports, isLoading } = useQuery({
        queryKey: ['identifikator', 'queue'],
        queryFn: getIdentifierQueue
    });

    // Fetch Articles for linking
    const { data: articlesData } = useQuery({
        queryKey: ['articles', 'all'],
        queryFn: () => getArticles('all'),
        enabled: newStatus === 'RESOLVED'
    });

    const articles = articlesData?.items || [];

    const resolveMutation = useMutation({
        mutationFn: () => {
            // P0 fix: payload matches AdminReportUpdateSchema
            const payload: AdminReportUpdatePayload = {
                status: newStatus,
                admin_note: adminNote || null,
                resolved_article_id: newStatus === 'RESOLVED' && resolvedArticleId
                    ? parseInt(resolvedArticleId)
                    : null,
            };
            return resolveMissingReport(selectedReport!.id, payload);
        },
        onSuccess: () => {
            notifications.show({ title: 'Prijava obrađena', message: 'Status je uspješno ažuriran.', color: 'green', icon: <IconCheck size={16} /> });
            queryClient.invalidateQueries({ queryKey: ['identifikator', 'queue'] });
            setResolveModalOpen(false);
            setNewStatus('RESOLVED');
            setAdminNote('');
            setResolvedArticleId(null);
        },
        onError: (err) => {
            notifications.show({ title: 'Greška', message: extractErrorMessage(err), color: 'red', icon: <IconX size={16} /> });
        }
    });

    const openResolve = (report: MissingItemReport) => {
        setSelectedReport(report);
        setResolveModalOpen(true);
    };

    const rows = reports?.map(report => (
        <Table.Tr key={report.id}>
            <Table.Td>{dayjs(report.created_at).format('DD.MM.YYYY HH:mm')}</Table.Td>
            <Table.Td fw={700}>{report.raw_input}</Table.Td>
            <Table.Td>{report.reported_by_user_id}</Table.Td>
            <Table.Td>
                <Badge color={STATUS_COLORS[report.status] || 'gray'}>
                    {report.status}
                </Badge>
            </Table.Td>
            <Table.Td>{report.admin_note || '-'}</Table.Td>
            <Table.Td>
                {(report.status === 'OPEN' || report.status === 'PENDING' || report.status === 'IN_REVIEW') && (
                    <Button size="xs" variant="light" onClick={() => openResolve(report)}>Obradi</Button>
                )}
            </Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="xl" py="xl">
            <Title order={2} mb="lg">Red čekanja — nedostajući artikli</Title>

            <div style={{ position: 'relative', minHeight: 200 }}>
                <LoadingOverlay visible={isLoading} />
                <Table striped highlightOnHover>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>Vrijeme</Table.Th>
                            <Table.Th>Unos</Table.Th>
                            <Table.Th>Korisnik (ID)</Table.Th>
                            <Table.Th>Status</Table.Th>
                            <Table.Th>Napomena</Table.Th>
                            <Table.Th>Akcija</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {rows}
                        {!isLoading && (!reports || reports.length === 0) && (
                            <Table.Tr>
                                <Table.Td colSpan={6}>
                                    <Text ta="center" c="dimmed" py="xl">Nema prijava u redu čekanja.</Text>
                                </Table.Td>
                            </Table.Tr>
                        )}
                    </Table.Tbody>
                </Table>
            </div>

            <Modal
                opened={resolveModalOpen}
                onClose={() => setResolveModalOpen(false)}
                title={`Obrada prijave: ${selectedReport?.raw_input}`}
            >
                <Stack>
                    <Select
                        label="Novi status"
                        data={[
                            { label: 'Riješeno (poveži s artiklom)', value: 'RESOLVED' },
                            { label: 'U obradi', value: 'IN_REVIEW' },
                            { label: 'Odbijeno / Nevažeće', value: 'REJECTED' },
                            { label: 'Zatvoreno', value: 'CLOSED' },
                        ]}
                        value={newStatus}
                        onChange={(v) => setNewStatus(v as AdminReportUpdatePayload['status'])}
                    />

                    {newStatus === 'RESOLVED' && (
                        <Select
                            label="Poveži s artiklom"
                            placeholder="Pretraži artikal..."
                            searchable
                            clearable
                            data={articles.map(a => ({ value: a.id.toString(), label: `${a.article_no} - ${a.description}` }))}
                            value={resolvedArticleId}
                            onChange={setResolvedArticleId}
                        />
                    )}

                    <Textarea
                        label="Administratorska napomena"
                        placeholder="Interna napomena..."
                        value={adminNote}
                        onChange={(e) => setAdminNote(e.currentTarget.value)}
                    />

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setResolveModalOpen(false)}>Odustani</Button>
                        <Button loading={resolveMutation.isPending} onClick={() => resolveMutation.mutate()}>Spremi</Button>
                    </Group>
                </Stack>
            </Modal>
        </Container>
    );
}
