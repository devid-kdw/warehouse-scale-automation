import { useState, useEffect } from 'react';
import {
    Container, Title, Paper, Table, Group, Button, TextInput,
    Badge, LoadingOverlay, Modal, NumberInput, Stack, Text
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    IconCheck,
    IconSearch, IconClipboardCheck, IconX,
} from '@tabler/icons-react';
import { getInventorySummary, performInventoryCount, extractErrorMessage } from '../api/services';
import { InventoryItem, InventoryCountPayload } from '../api/types';
import { EmptyState } from '../components/common/EmptyState';
import { getExpiryStatus } from '../utils/expiry';
import dayjs from 'dayjs';

// --- Count Modal Component ---
function CountModal({ item, opened, onClose }: { item: InventoryItem | null, opened: boolean, onClose: () => void }) {
    const queryClient = useQueryClient();

    const form = useForm({
        initialValues: {
            counted_qty: 0,
            note: '',
        },
        validate: {
            counted_qty: (val) => val < 0 ? 'Quantity cannot be negative' : null,
        },
    });

    // Reset form when item changes
    useEffect(() => {
        if (item) {
            form.setFieldValue('counted_qty', item.total_qty);
            form.setFieldValue('note', '');
        }
    }, [item]);

    const countMutation = useMutation({
        mutationFn: (values: typeof form.values) => {
            const payload: InventoryCountPayload = {
                location_id: item!.location_id,
                article_id: item!.article_id,
                batch_id: item!.batch_id,
                counted_total_qty: values.counted_qty,
                note: values.note,
                client_event_id: crypto.randomUUID(),
            };
            return performInventoryCount(payload);
        },
        onSuccess: () => {
            notifications.show({ title: 'Success', message: 'Inventory count recorded', color: 'green', icon: <IconCheck size={16} /> });
            queryClient.invalidateQueries({ queryKey: ['inventory'] });
            onClose();
            form.reset();
        },
        onError: (err) => {
            notifications.show({ title: 'Error', message: extractErrorMessage(err), color: 'red', icon: <IconX size={16} /> });
        }
    });

    // Reset logic moved to useEffect

    return (
        <Modal opened={opened} onClose={onClose} title="Perform Inventory Count" centered>
            <form onSubmit={form.onSubmit((values) => countMutation.mutate(values))}>
                <Stack>
                    <Text size="sm">
                        <b>Article:</b> {item?.article_no} - {item?.description} <br />
                        <b>Batch:</b> {item?.batch_code} <br />
                        <b>Location:</b> {item?.location_code}
                    </Text>

                    <NumberInput
                        label="Counted Quantity (Total)"
                        description={`Current System Qty: ${item?.total_qty} KG`}
                        decimalScale={2}
                        min={0}
                        {...form.getInputProps('counted_qty')}
                    />

                    <TextInput
                        label="Note"
                        placeholder="Reason for discrepancy..."
                        {...form.getInputProps('note')}
                    />

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={onClose}>Cancel</Button>
                        <Button type="submit" loading={countMutation.isPending} leftSection={<IconClipboardCheck size={16} />}>
                            Submit Count
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
}

export default function Inventory() {
    const [search, setSearch] = useState('');
    const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
    const [opened, { open, close }] = useDisclosure(false);

    // Fetch Inventory
    const { data, isLoading } = useQuery({
        queryKey: ['inventory'],
        queryFn: () => getInventorySummary(),
    });

    // Filter logic
    const filteredItems = data?.items.filter(item =>
        item.article_no.toLowerCase().includes(search.toLowerCase()) ||
        (item.description || '').toLowerCase().includes(search.toLowerCase()) ||
        item.batch_code.toLowerCase().includes(search.toLowerCase()) ||
        item.location_code.toLowerCase().includes(search.toLowerCase())
    ) || [];

    const openCountModal = (item: InventoryItem) => {
        setSelectedItem(item);
        open();
    };

    const rows = filteredItems.map((item) => {
        const expiryStatus = getExpiryStatus(item.expiry_date);

        return (
            <Table.Tr key={`${item.location_id}-${item.article_id}-${item.batch_id}`}>
                <Table.Td>{item.location_code}</Table.Td>
                <Table.Td>
                    <Text size="sm" fw={500}>{item.article_no}</Text>
                    <Text size="xs" c="dimmed">{item.description}</Text>
                </Table.Td>
                <Table.Td>{item.batch_code}</Table.Td>
                <Table.Td>
                    {item.expiry_date ? (
                        <Badge
                            color={expiryStatus === 'expired' ? 'red' : (expiryStatus === 'soon' ? 'orange' : 'gray')}
                            variant={expiryStatus === 'expired' ? 'filled' : 'light'}
                        >
                            {dayjs(item.expiry_date).format('DD.MM.YYYY')}
                        </Badge>
                    ) : '-'}
                </Table.Td>
                <Table.Td fw={700}>{item.stock_qty.toFixed(2)}</Table.Td>
                <Table.Td>{item.surplus_qty.toFixed(2)}</Table.Td>
                <Table.Td fw={900} c="blue">{item.total_qty.toFixed(2)}</Table.Td>
                <Table.Td>
                    <Button
                        size="xs"
                        variant="subtle"
                        leftSection={<IconClipboardCheck size={14} />}
                        onClick={() => openCountModal(item)}
                    >
                        Count
                    </Button>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Inventory Overview</Title>
                <Button leftSection={<IconClipboardCheck size={16} />} disabled>
                    Full Stocktake
                </Button>
            </Group>

            <Paper shadow="xs" p="md" withBorder>
                <TextInput
                    placeholder="Search by article, batch, or location..."
                    leftSection={<IconSearch size={16} />}
                    mb="md"
                    value={search}
                    onChange={(e) => setSearch(e.currentTarget.value)}
                />

                <div style={{ position: 'relative', minHeight: 200 }}>
                    <LoadingOverlay visible={isLoading} />

                    {filteredItems.length === 0 && !isLoading ? (
                        <EmptyState message="No inventory items found" />
                    ) : (
                        <Table striped highlightOnHover>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Location</Table.Th>
                                    <Table.Th>Article</Table.Th>
                                    <Table.Th>Batch</Table.Th>
                                    <Table.Th>Expiry</Table.Th>
                                    <Table.Th>Stock (KG)</Table.Th>
                                    <Table.Th>Surplus (KG)</Table.Th>
                                    <Table.Th>Total (KG)</Table.Th>
                                    <Table.Th w={100}></Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>{rows}</Table.Tbody>
                        </Table>
                    )}
                </div>
            </Paper>

            <CountModal
                item={selectedItem}
                opened={opened}
                onClose={() => { close(); setSelectedItem(null); }}
            />
        </Container>
    );
}
