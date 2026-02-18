
import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text,
    Badge, LoadingOverlay, ScrollArea, Drawer,
    Stack, Card, NumberInput, ActionIcon
} from '@mantine/core';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getDailyDrafts, getDailyDraftDetail,
    approveDailyDrafts, rejectDailyDrafts, updateDailyDraftLines,
    extractErrorMessage
} from '../../api/services';
import { IconEye, IconCheck, IconX, IconEdit } from '@tabler/icons-react';
import { EmptyState } from '../../components/common/EmptyState';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import { notifications } from '@mantine/notifications';

export default function DraftApproval() {
    const { t } = useTranslation('common');
    const queryClient = useQueryClient();
    const [selectedDay, setSelectedDay] = useState<{ date: string, location_id: number } | null>(null);

    // Fetch Daily Drafts List
    const { data: dailyDrafts, isLoading } = useQuery({
        queryKey: ['dailyDrafts'],
        queryFn: () => getDailyDrafts(),
    });

    const approveMutation = useMutation({
        mutationFn: ({ date, location_id }: { date: string, location_id: number }) =>
            approveDailyDrafts(date, location_id),
        onSuccess: () => {
            notifications.show({ title: t('common.success'), message: t('approvals.successApprove'), color: 'green' });
            queryClient.invalidateQueries({ queryKey: ['dailyDrafts'] });
            setSelectedDay(null);
        },
        onError: (err) => notifications.show({ title: t('common.error'), message: extractErrorMessage(err), color: 'red' })
    });

    const rejectMutation = useMutation({
        mutationFn: ({ date, location_id }: { date: string, location_id: number }) =>
            rejectDailyDrafts(date, location_id),
        onSuccess: () => {
            notifications.show({ title: t('common.success'), message: t('approvals.successReject'), color: 'green' });
            queryClient.invalidateQueries({ queryKey: ['dailyDrafts'] });
            setSelectedDay(null);
        },
        onError: (err) => notifications.show({ title: t('common.error'), message: extractErrorMessage(err), color: 'red' })
    });

    // P0 fix: backend DailyApprovalSummarySchema returns total_lines + total_qty (not draft_count / status)
    const rows = dailyDrafts?.map((day: any) => (
        <Table.Tr key={`${day.date}-${day.location_id}`} style={{ cursor: 'pointer' }} onClick={() => setSelectedDay(day)}>
            <Table.Td>{dayjs(day.date).format('DD.MM.YYYY')}</Table.Td>
            <Table.Td>{day.location_code || day.location_id}</Table.Td>
            <Table.Td>{day.total_lines ?? '-'}</Table.Td>
            <Table.Td>{day.total_qty != null ? `${day.total_qty.toFixed(2)}` : '-'}</Table.Td>
            <Table.Td>
                <Button size="compact-xs" variant="subtle" leftSection={<IconEye size={14} />}>
                    {t('approvals.viewDetails')}
                </Button>
            </Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="xl" py="xl" className="page-container">
            <Group justify="space-between" mb="lg">
                <Title order={2}>{t('approvals.title')}</Title>
            </Group>

            <Paper shadow="xs" p="md" withBorder>
                <LoadingOverlay visible={isLoading} />

                {dailyDrafts?.length === 0 ? (
                    <EmptyState message={t('approvals.noDrafts')} />
                ) : (
                    <Table stickyHeader striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>{t('approvals.date')}</Table.Th>
                                <Table.Th>{t('approvals.location')}</Table.Th>
                                {/* P0 fix: total_lines replaces draft_count */}
                                <Table.Th>Broj stavki</Table.Th>
                                {/* P0 fix: total_qty replaces status */}
                                <Table.Th>Ukupna kol.</Table.Th>
                                <Table.Th>{t('approvals.actions')}</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <Drawer
                opened={!!selectedDay}
                onClose={() => setSelectedDay(null)}
                title={selectedDay ? t('approvals.detailsTitle', { date: dayjs(selectedDay.date).format('DD.MM.YYYY') }) : ''}
                position="right"
                size="xl"
            >
                {selectedDay && (
                    <DailyDetailView
                        date={selectedDay.date}
                        locationId={selectedDay.location_id}
                        onApprove={() => approveMutation.mutate(selectedDay)}
                        onReject={() => rejectMutation.mutate(selectedDay)}
                        isProcessing={approveMutation.isPending || rejectMutation.isPending}
                    />
                )}
            </Drawer>
        </Container>
    );
}

function DailyDetailView({ date, locationId, onApprove, onReject, isProcessing }: any) {
    const { t } = useTranslation('common');
    const queryClient = useQueryClient();
    // P0 fix: backend returns flat list (many=True), not { groups: [...] }
    const { data: detailLines, isLoading } = useQuery({
        queryKey: ['dailyDraftDetail', date, locationId],
        queryFn: () => getDailyDraftDetail(date, locationId),
    });

    const updateLineMutation = useMutation({
        mutationFn: async ({ article_id, batch_id, quantity }: { article_id: number, batch_id: number | null, quantity: number }) => {
            if (batch_id === null) throw new Error('batch_id je obavezan');
            return updateDailyDraftLines(date, locationId, {
                article_id,
                batch_id,
                new_total_qty: quantity
            });
        },
        onSuccess: () => {
            notifications.show({ title: t('common.success'), message: t('common.saved'), color: 'green' });
            queryClient.invalidateQueries({ queryKey: ['dailyDraftDetail', date, locationId] });
        },
        onError: (err) => notifications.show({ title: t('common.error'), message: extractErrorMessage(err), color: 'red' })
    });

    if (isLoading) return <LoadingOverlay visible />;

    // P0 fix: detailLines is a flat array (not detailData.groups)
    const lines: any[] = Array.isArray(detailLines) ? detailLines : [];

    return (
        <Stack h="calc(100vh - 80px)">
            <ScrollArea flex={1}>
                {lines.length === 0 && (
                    <Text c="dimmed" ta="center" py="xl">Nema stavki za ovaj dan.</Text>
                )}
                {lines.map((line: any) => (
                    <DraftGroupCard
                        key={`${line.article_id}-${line.batch_id}`}
                        group={line}
                        onUpdate={(qty: number) => updateLineMutation.mutate({
                            article_id: line.article_id,
                            batch_id: line.batch_id,
                            quantity: qty
                        })}
                        isUpdating={updateLineMutation.isPending}
                    />
                ))}
            </ScrollArea>

            <Paper p="md" withBorder style={{ borderTop: '1px solid #eee' }}>
                <Group grow>
                    <Button color="red" variant="light" onClick={onReject} loading={isProcessing} leftSection={<IconX size={16} />}>
                        {t('approvals.rejectDay')}
                    </Button>
                    <Button color="green" onClick={onApprove} loading={isProcessing} leftSection={<IconCheck size={16} />}>
                        {t('approvals.approveDay')}
                    </Button>
                </Group>
            </Paper>
        </Stack>
    );
}

function DraftGroupCard({ group, onUpdate, isUpdating }: any) {
    const { t } = useTranslation('common');
    const [editing, setEditing] = useState(false);
    // P0 fix: backend field is total_qty (not total_quantity)
    const [val, setVal] = useState<number>(group.total_qty ?? 0);

    return (
        <Card withBorder mb="sm" padding="sm">
            <Group justify="space-between" mb="xs">
                <Text fw={500}>{group.article_no} - {group.article_name}</Text>
                <Badge variant="outline">{group.batch_code || 'N/A'}</Badge>
            </Group>
            <Group justify="space-between" align="center">
                <Group gap="xs">
                    {/* P0 fix: draft_ids is an array; use its length for count */}
                    <Text size="sm">{t('approvals.draftCount')}: {group.draft_ids?.length ?? 0}</Text>
                </Group>

                <Group gap="xs">
                    {editing ? (
                        <NumberInput
                            value={val}
                            onChange={(v: string | number) => setVal(Number(v))}
                            size="xs"
                            style={{ width: 100 }}
                            decimalScale={2}
                        />
                    ) : (
                        // P0 fix: total_qty (not total_quantity)
                        <Text size="sm" fw={700}>{group.total_qty} {group.uom}</Text>
                    )}

                    {editing ? (
                        <ActionIcon color="green" variant="light" size="sm" onClick={() => {
                            onUpdate(val);
                            setEditing(false);
                        }} loading={isUpdating}>
                            <IconCheck size={14} />
                        </ActionIcon>
                    ) : (
                        <ActionIcon color="blue" variant="subtle" size="sm" onClick={() => {
                            setVal(group.total_qty ?? 0);
                            setEditing(true);
                        }}>
                            <IconEdit size={14} />
                        </ActionIcon>
                    )}
                </Group>
            </Group>
        </Card>
    );
}
