import { useState } from 'react';
import {
    Container, Paper, Title, Table, Button, Group, Text, Alert,
    Badge, LoadingOverlay, SegmentedControl, ActionIcon
} from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { getDraftGroups, extractErrorMessage } from '../../api/services';
import { IconAlertCircle, IconEye, IconEdit } from '@tabler/icons-react';
import { EmptyState } from '../../components/common/EmptyState';
import DraftGroupDetail from '../Approvals/DraftGroupDetail';
import dayjs from 'dayjs';

export default function DraftApproval() {
    const [statusFilter, setStatusFilter] = useState<string>('DRAFT');
    const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null);

    // Fetch Draft Groups instead of individual drafts
    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['draftGroups', statusFilter],
        queryFn: () => getDraftGroups(statusFilter),
    });

    const rows = data?.items.map((group) => {
        const sourceLabel = group.source === 'ui_admin' ? 'Admin Draft' : 'Auto Draft';
        const sourceColor = group.source === 'ui_admin' ? 'blue' : 'gray';

        return (
            <Table.Tr key={group.id} style={{ cursor: 'pointer' }} onClick={() => setSelectedGroupId(group.id)}>
                <Table.Td>{group.id}</Table.Td>
                <Table.Td>{dayjs(group.created_at).format('DD.MM.YYYY HH:mm')}</Table.Td>
                <Table.Td>
                    <Group gap="xs">
                        <Text size="sm" fw={500}>{group.name || '(unnamed group)'}</Text>
                        <ActionIcon
                            size="xs"
                            variant="subtle"
                            color="blue"
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedGroupId(group.id);
                            }}
                        >
                            <IconEdit size={14} />
                        </ActionIcon>
                    </Group>
                    <Text size="xs" c="dimmed">{group.line_count} items</Text>
                </Table.Td>
                <Table.Td fw={700}>{group.total_quantity_kg} kg</Table.Td>
                <Table.Td>
                    <Badge
                        color={group.status === 'DRAFT' ? 'blue' : (group.status === 'APPROVED' ? 'green' : 'red')}
                        variant="light"
                    >
                        {group.status}
                    </Badge>
                </Table.Td>
                <Table.Td>
                    <Badge color={sourceColor} variant="dot">
                        {sourceLabel}
                    </Badge>
                </Table.Td>
                <Table.Td>
                    <Button size="compact-xs" variant="subtle" leftSection={<IconEye size={14} />}>
                        View Details
                    </Button>
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
                <Alert icon={<IconAlertCircle size={16} />} title="Error loading draft groups" color="red" mb="md">
                    {extractErrorMessage(error)}
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <LoadingOverlay visible={isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

                {(data?.items.length === 0 || !data) ? (
                    <EmptyState message={`No ${statusFilter.toLowerCase()} draft groups found.`} />
                ) : (
                    <Table stickyHeader striped highlightOnHover withTableBorder>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>ID</Table.Th>
                                <Table.Th>Created At</Table.Th>
                                <Table.Th>Name / Items</Table.Th>
                                <Table.Th>Total Qty</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>Source</Table.Th>
                                <Table.Th>Actions</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                )}
            </Paper>

            <DraftGroupDetail
                groupId={selectedGroupId}
                onClose={() => setSelectedGroupId(null)}
            />
        </Container>
    );
}
