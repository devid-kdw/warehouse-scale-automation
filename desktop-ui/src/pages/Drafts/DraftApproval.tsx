import { useState, useMemo } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text, Alert,
    Modal, Textarea, Badge, LoadingOverlay, Stack, SegmentedControl, Code
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';
import { getDrafts, approveDraft, rejectDraft, extractErrorMessage, getArticles } from '../../api/services';
import { WeighInDraft, Article } from '../../api/types';
import { LoadingState } from '../../components/common/LoadingState';
import { EmptyState } from '../../components/common/EmptyState';

export default function DraftApproval() {
    const queryClient = useQueryClient();
    const [selectedDraft, setSelectedDraft] = useState<WeighInDraft | null>(null);
    const [approvalNote, setApprovalNote] = useState('');
    const [opened, { open, close }] = useDisclosure(false);
    const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');
    const [statusFilter, setStatusFilter] = useState<string>('DRAFT');

    // Fetch Articles for mapping
    const articlesQuery = useQuery({
        queryKey: ['articles', 'all'],
        queryFn: () => getArticles('all'),
        staleTime: 1000 * 60 * 5, // 5 min
    });

    const articleMap = useMemo(() => {
        const map = new Map<number, Article>();
        articlesQuery.data?.items.forEach(a => map.set(a.id, a));
        return map;
    }, [articlesQuery.data]);

    // Fetch Drafts
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['drafts', statusFilter],
        queryFn: () => getDrafts(statusFilter),
    });

    // Approve/Reject Mutation
    const mutation = useMutation({
        mutationFn: async () => {
            if (!selectedDraft) return;
            const payload = { note: approvalNote };

            if (actionType === 'approve') {
                return approveDraft(selectedDraft.id, payload);
            } else {
                return rejectDraft(selectedDraft.id, payload);
            }
        },
        onSuccess: (data) => {
            notifications.show({
                title: actionType === 'approve' ? 'Approved' : 'Rejected',
                message: `Draft #${selectedDraft?.id} processed successfully.`,
                color: 'green',
                icon: <IconCheck size={16} />,
            });
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
            close();
            setApprovalNote('');
            setSelectedDraft(null);
        },
        onError: (err: any) => {
            // If 409 conflict (insufficient stock), the error message should be detailed enough via extractErrorMessage
            notifications.show({
                title: 'Action Failed',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />,
                autoClose: 10000, // Keep longer for errors
            });
        }
    });

    const handleAction = (draft: WeighInDraft, type: 'approve' | 'reject') => {
        setSelectedDraft(draft);
        setActionType(type);
        setApprovalNote('');
        open();
    };

    const rows = data?.items.map((draft) => {
        const article = articleMap.get(draft.article_id);
        const articleDisplay = article ? `${article.article_no} - ${article.description}` : `ID: ${draft.article_id}`;

        return (
            <Table.Tr key={draft.id}>
                <Table.Td>{draft.id}</Table.Td>
                <Table.Td>{new Date(draft.created_at).toLocaleString()}</Table.Td>
                <Table.Td>
                    <Text size="sm" fw={500}>{articleDisplay}</Text>
                    <Text size="xs" c="dimmed">Batch ID: {draft.batch_id}</Text>
                </Table.Td>
                <Table.Td fw={700}>{draft.quantity_kg} kg</Table.Td>
                <Table.Td>
                    <Badge
                        color={draft.status === 'DRAFT' ? 'blue' : (draft.status === 'APPROVED' ? 'green' : 'red')}
                        variant="light"
                    >
                        {draft.status}
                    </Badge>
                </Table.Td>
                <Table.Td>
                    <Code>{draft.source || 'manual'}</Code>
                </Table.Td>
                <Table.Td>
                    {draft.status === 'DRAFT' && (
                        <Group gap="xs">
                            <Button size="compact-xs" color="green" variant="light" onClick={() => handleAction(draft, 'approve')}>
                                Approve
                            </Button>
                            <Button size="compact-xs" color="red" variant="subtle" onClick={() => handleAction(draft, 'reject')}>
                                Reject
                            </Button>
                        </Group>
                    )}
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Draft Approvals</Title>
                <SegmentedControl
                    value={statusFilter}
                    onChange={setStatusFilter}
                    data={[
                        { label: 'Pending', value: 'DRAFT' },
                        { label: 'Approved', value: 'APPROVED' },
                        { label: 'Rejected', value: 'REJECTED' },
                    ]}
                />
            </Group>

            {isError && (
                <Alert icon={<IconAlertCircle size={16} />} title="Error loading drafts" color="red" mb="md">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <LoadingOverlay visible={isLoading || articlesQuery.isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

                {data?.items.length === 0 ? (
                    <EmptyState message={`No ${statusFilter.toLowerCase()} drafts found.`} />
                ) : (
                    <Table stickyHeader striped highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Timestamp</Table.Th>
                                <Table.Th>Article / Batch</Table.Th>
                                <Table.Th>Quantity</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>Source</Table.Th>
                                <Table.Th>Actions</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <Modal opened={opened} onClose={close} title={`${actionType === 'approve' ? 'Approve' : 'Reject'} Draft #${selectedDraft?.id}`} centered>
                <Stack>
                    <Text size="sm">
                        Are you sure you want to <strong>{actionType}</strong> this draft?
                    </Text>

                    {selectedDraft && (
                        <Paper withBorder p="xs" bg="gray.1">
                            <Group justify="space-between">
                                <Text size="xs" fw={700}>Quantity:</Text>
                                <Text size="xs">{selectedDraft.quantity_kg} kg</Text>
                            </Group>
                            <Group justify="space-between">
                                <Text size="xs" fw={700}>Article ID:</Text>
                                <Text size="xs">{selectedDraft.article_id}</Text>
                            </Group>
                            <Group justify="space-between">
                                <Text size="xs" fw={700}>Batch ID:</Text>
                                <Text size="xs">{selectedDraft.batch_id}</Text>
                            </Group>
                        </Paper>
                    )}

                    <Textarea
                        label="Note"
                        placeholder="Optional reason or comment"
                        value={approvalNote}
                        onChange={(e) => setApprovalNote(e.target.value)}
                        minRows={3}
                    />

                    {mutation.isError && (
                        <Alert color="red" title="Error" icon={<IconAlertCircle size={16} />}>
                            {extractErrorMessage(mutation.error)}
                        </Alert>
                    )}

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={close}>Cancel</Button>
                        <Button
                            color={actionType === 'approve' ? 'green' : 'red'}
                            loading={mutation.isPending}
                            onClick={() => mutation.mutate()}
                        >
                            Confirm {actionType === 'approve' ? 'Approval' : 'Rejection'}
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Container>
    );
}
