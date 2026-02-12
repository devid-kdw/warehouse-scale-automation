import { Modal, Table, Group, Text, Button, Stack, Badge, TextInput, LoadingOverlay, Alert, Paper, ActionIcon } from '@mantine/core';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDraftGroup, approveDraftGroup, rejectDraftGroup, renameDraftGroup, extractErrorMessage } from '../../api/services';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX, IconAlertCircle, IconEdit } from '@tabler/icons-react';
import { useState, useEffect } from 'react';

interface Props {
    groupId: number | null;
    onClose: () => void;
}

export default function DraftGroupDetail({ groupId, onClose }: Props) {
    const queryClient = useQueryClient();
    const [isEditingName, setIsEditingName] = useState(false);
    const [newName, setNewName] = useState('');

    const { data: group, isLoading, isError, error } = useQuery({
        queryKey: ['draftGroup', groupId],
        queryFn: () => getDraftGroup(groupId!),
        enabled: !!groupId,
    });

    useEffect(() => {
        if (group) {
            setNewName(group.name);
        }
    }, [group]);

    const renameMutation = useMutation({
        mutationFn: () => renameDraftGroup(groupId!, newName),
        onSuccess: () => {
            notifications.show({ title: 'Success', message: 'Group renamed', color: 'green' });
            setIsEditingName(false);
            queryClient.invalidateQueries({ queryKey: ['draftGroup', groupId] });
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
        },
        onError: (err) => notifications.show({ title: 'Error', message: extractErrorMessage(err), color: 'red' })
    });

    const approveMutation = useMutation({
        mutationFn: () => approveDraftGroup(groupId!),
        onSuccess: () => {
            notifications.show({ title: 'Approved', message: 'Group approved successfully', color: 'green', icon: <IconCheck size={16} /> });
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
            queryClient.invalidateQueries({ queryKey: ['inventory'] });
            onClose();
        },
        onError: (err) => notifications.show({ title: 'Approval Failed', message: extractErrorMessage(err), color: 'red', icon: <IconX size={16} />, autoClose: 10000 })
    });

    const rejectMutation = useMutation({
        mutationFn: () => rejectDraftGroup(groupId!),
        onSuccess: () => {
            notifications.show({ title: 'Rejected', message: 'Group rejected', color: 'gray' });
            queryClient.invalidateQueries({ queryKey: ['draftGroups'] });
            onClose();
        },
        onError: (err) => notifications.show({ title: 'Rejection Failed', message: extractErrorMessage(err), color: 'red' })
    });

    const canAction = group?.status === 'DRAFT';

    return (
        <Modal
            opened={!!groupId}
            onClose={onClose}
            title={
                <Group gap="xs">
                    <Text fw={700}>Draft Group #{groupId}</Text>
                    <Badge color={group?.status === 'DRAFT' ? 'blue' : group?.status === 'APPROVED' ? 'green' : 'red'}>
                        {group?.status}
                    </Badge>
                </Group>
            }
            size="xl"
        >
            <LoadingOverlay visible={isLoading} />

            {isError && (
                <Alert color="red" icon={<IconAlertCircle size={16} />} title="Error">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            {group && (
                <Stack>
                    <Paper withBorder p="md">
                        <Group justify="space-between" align="flex-end">
                            <Stack gap={0}>
                                <Text size="xs" c="dimmed" fw={700}>GROUP NAME</Text>
                                {isEditingName ? (
                                    <Group gap="xs">
                                        <TextInput
                                            size="xs"
                                            value={newName}
                                            onChange={(e) => setNewName(e.target.value)}
                                            autoFocus
                                        />
                                        <Button size="compact-xs" loading={renameMutation.isPending} onClick={() => renameMutation.mutate()}>Save</Button>
                                        <Button size="compact-xs" variant="subtle" onClick={() => setIsEditingName(false)}>Cancel</Button>
                                    </Group>
                                ) : (
                                    <Group gap="xs">
                                        <Text fw={500}>{group.name || '(unnamed)'}</Text>
                                        {canAction && (
                                            <ActionIcon size="xs" variant="subtle" onClick={() => setIsEditingName(true)}>
                                                <IconEdit size={14} />
                                            </ActionIcon>
                                        )}
                                    </Group>
                                )}
                            </Stack>
                            <Stack gap={0} align="flex-end">
                                <Text size="xs" c="dimmed" fw={700}>SOURCE</Text>
                                <Badge variant="dot" color={group.source === 'ui_admin' ? 'blue' : 'gray'}>
                                    {group.source}
                                </Badge>
                            </Stack>
                        </Group>
                    </Paper>

                    <Table striped highlightOnHover withTableBorder>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Article ID</Table.Th>
                                <Table.Th>Batch ID</Table.Th>
                                <Table.Th>Quantity</Table.Th>
                                <Table.Th>Note</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {(group.drafts || group.lines)?.map((line) => (
                                <Table.Tr key={line.id}>
                                    <Table.Td>{line.article_id}</Table.Td>
                                    <Table.Td>{line.batch_id}</Table.Td>
                                    <Table.Td fw={700}>{line.quantity_kg} kg</Table.Td>
                                    <Table.Td>{line.note}</Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={onClose}>Close</Button>
                        {canAction && (
                            <>
                                <Button color="red" variant="light" loading={rejectMutation.isPending} onClick={() => rejectMutation.mutate()}>
                                    Reject Group
                                </Button>
                                <Button color="green" loading={approveMutation.isPending} onClick={() => approveMutation.mutate()}>
                                    Approve Group
                                </Button>
                            </>
                        )}
                    </Group>
                </Stack>
            )}
        </Modal>
    );
}
