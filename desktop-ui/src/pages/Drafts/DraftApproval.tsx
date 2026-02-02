import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text, Alert,
    Modal, Textarea, Badge, LoadingOverlay, Stack
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconCheck, IconX, IconEye } from '@tabler/icons-react';
import { getDrafts, approveDraft, rejectDraft, extractErrorMessage } from '../../api/services';
import { WeighInDraft } from '../../api/types';
import { STORAGE_KEYS } from '../../api/client';

export default function DraftApproval() {
    const queryClient = useQueryClient();
    const [selectedDraft, setSelectedDraft] = useState<WeighInDraft | null>(null);
    const [approvalNote, setApprovalNote] = useState('');
    const [opened, { open, close }] = useDisclosure(false);
    const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');

    // Fetch Pending Drafts
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['drafts', 'pending'],
        queryFn: () => getDrafts('DRAFT'),
    });

    const getActorId = () => {
        const id = localStorage.getItem(STORAGE_KEYS.ACTOR_ID);
        return id ? parseInt(id) : 1;
    };

    // Approve/Reject Mutation
    const mutation = useMutation({
        mutationFn: async () => {
            if (!selectedDraft) return;
            const payload = { actor_user_id: getActorId(), note: approvalNote };

            if (actionType === 'approve') {
                return approveDraft(selectedDraft.id, payload);
            } else {
                return rejectDraft(selectedDraft.id, payload);
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['drafts'] });
            close();
            setApprovalNote('');
            setSelectedDraft(null);
        },
    });

    const handleAction = (draft: WeighInDraft, type: 'approve' | 'reject') => {
        setSelectedDraft(draft);
        setActionType(type);
        setApprovalNote('');
        open();
    };

    const rows = data?.items.map((draft) => (
        <Table.Tr key={draft.id}>
            <Table.Td>{draft.id}</Table.Td>
            <Table.Td>{draft.article_id} (Batch {draft.batch_id})</Table.Td>
            <Table.Td fw={700}>{draft.quantity_kg} kg</Table.Td>
            <Table.Td>
                <Badge color={draft.status === 'DRAFT' ? 'enikonBlue.3' : (draft.status === 'APPROVED' ? 'enikonBlue.4' : 'gray')}>{draft.status}</Badge>
            </Table.Td>
            <Table.Td>{new Date(draft.created_at).toLocaleString()}</Table.Td>
            <Table.Td>
                <Group gap="xs">
                    <Button size="xs" color="enikonBlue.6" variant="filled" onClick={() => handleAction(draft, 'approve')}>
                        Approve
                    </Button>
                    <Button size="xs" color="gray" variant="light" onClick={() => handleAction(draft, 'reject')}>
                        Reject
                    </Button>
                </Group>
            </Table.Td>
        </Table.Tr>
    ));

    return (
        <Container size="lg" py="xl">
            <Title order={2} mb="lg">Draft Approvals</Title>

            {isError && (
                <Alert icon={<IconX size={16} />} title="Error loading drafts" color="red" mb="md">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <LoadingOverlay visible={isLoading} />
                {data?.items.length === 0 ? (
                    <Text c="dimmed" ta="center" py="xl">No pending drafts found.</Text>
                ) : (
                    <Table stickyHeader>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Article / Batch</Table.Th>
                                <Table.Th>Quantity</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>Time</Table.Th>
                                <Table.Th>Actions</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <Modal opened={opened} onClose={close} title={`${actionType === 'approve' ? 'Approve' : 'Reject'} Draft #${selectedDraft?.id}`}>
                <Stack>
                    <Text size="sm">
                        Are you sure you want to <strong>{actionType}</strong> this draft?
                        <br />
                        Quantity: {selectedDraft?.quantity_kg} kg
                    </Text>

                    <Textarea
                        label="Note"
                        placeholder="Optional reason or comment"
                        value={approvalNote}
                        onChange={(e) => setApprovalNote(e.target.value)}
                    />

                    {mutation.isError && (
                        <Alert color="red" title="Error">
                            {extractErrorMessage(mutation.error)}
                        </Alert>
                    )}

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={close}>Cancel</Button>
                        <Button
                            color={actionType === 'approve' ? 'enikonBlue.6' : 'red'}
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
