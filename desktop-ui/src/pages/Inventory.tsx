import { useState, useEffect } from 'react';
import {
    Container, Title, Paper, Table, Group, Button, TextInput,
    Badge, LoadingOverlay, Modal, NumberInput, Stack, Text,
    Menu, ActionIcon, Tooltip, Select, SegmentedControl, Alert
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    IconCheck,
    IconSearch, IconClipboardCheck, IconX, IconDotsVertical, IconPackageImport, IconAlertTriangle,
    IconRefresh, IconPlus, IconEdit, IconArchive, IconTag
} from '@tabler/icons-react';
import {
    getInventory, performInventoryCount, extractErrorMessage,
    archiveArticle, getArticles
} from '../api/services';
import { InventoryItem, InventoryCountPayload, Article } from '../api/types';
import { EmptyState } from '../components/common/EmptyState';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ArticleForm } from './Inventory/components/ArticleForm';
import { AliasesEditor } from './Inventory/components/AliasesEditor';

dayjs.extend(relativeTime);

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

    return (
        <Modal opened={opened} onClose={onClose} title="Popis zaliha" centered>
            <form onSubmit={form.onSubmit((values) => countMutation.mutate(values))}>
                <Stack>
                    <Text size="sm">
                        <b>Artikl:</b> {item?.article_no} - {item?.description} <br />
                        <b>Šarža:</b> {item?.batch_code} <br />
                        <b>Lokacija:</b> {item?.location_code}
                    </Text>

                    <NumberInput
                        label="Prebrojana količina (ukupno)"
                        description={`Trenutna sistemska kol.: ${item?.total_qty}`}
                        decimalScale={2}
                        min={0}
                        {...form.getInputProps('counted_qty')}
                    />

                    <TextInput
                        label="Napomena"
                        placeholder="Razlog odstupanja..."
                        {...form.getInputProps('note')}
                    />

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={onClose}>Odustani</Button>
                        <Button type="submit" loading={countMutation.isPending} leftSection={<IconClipboardCheck size={16} />}>
                            Spremi popis
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
}

export default function Inventory() {
    const navigate = useNavigate();
    const auth = useAuth();
    const isAdmin = auth.user?.role === 'ADMIN';
    const queryClient = useQueryClient();

    // State
    const [search, setSearch] = useState('');
    // P1 fix: category Select replaces Paint/Consumables tabs
    const [category, setCategory] = useState<string | null>(null);
    // P1 fix: state filter (active/inactive/all)
    const [stateFilter, setStateFilter] = useState<'active' | 'inactive' | 'all'>('active');

    const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
    const [countModalOpened, { open: openCountModal, close: closeCountModal }] = useDisclosure(false);

    // Article Management State
    const [articleFormOpened, { open: openArticleForm, close: closeArticleForm }] = useDisclosure(false);
    const [aliasesOpened, { open: openAliases, close: closeAliases }] = useDisclosure(false);
    const [editingArticle, setEditingArticle] = useState<Article | null>(null);

    // Fetch Inventory — pass category + state to API
    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['inventory', category, stateFilter],
        queryFn: () => getInventory({
            category: category || undefined,
            state: stateFilter,
            search: undefined // client-side search
        }),
    });

    // Client-side search filtering
    const filteredItems = data?.items.filter(item => {
        if (!search) return true;
        const s = search.toLowerCase();
        return item.article_no.toLowerCase().includes(s) ||
            (item.description || '').toLowerCase().includes(s) ||
            item.batch_code.toLowerCase().includes(s) ||
            (item.manufacturer || '').toLowerCase().includes(s);
    }) || [];

    const handleEditArticle = async (item: InventoryItem) => {
        try {
            const response = await queryClient.fetchQuery({
                queryKey: ['article', item.article_no],
                queryFn: () => getArticles('all').then(res => res.items.find(a => a.id === item.article_id))
            });

            if (response) {
                setEditingArticle(response);
                openArticleForm();
            } else {
                notifications.show({ title: 'Greška', message: 'Detalji artikla nisu pronađeni', color: 'red' });
            }
        } catch (e) {
            notifications.show({ title: 'Greška', message: 'Nije moguće učitati detalje artikla', color: 'red' });
        }
    };

    const handleArchiveArticle = async (articleId: number) => {
        if (confirm('Jeste li sigurni da želite arhivirati ovaj artikl?')) {
            try {
                await archiveArticle(articleId);
                notifications.show({ title: 'Uspjeh', message: 'Artikl arhiviran', color: 'green' });
                refetch();
            } catch (e) {
                notifications.show({ title: 'Greška', message: 'Arhiviranje nije uspjelo', color: 'red' });
            }
        }
    };

    const handleAliases = async (item: InventoryItem) => {
        setEditingArticle({
            id: item.article_id,
            article_no: item.article_no,
            description: item.description || '',
            is_paint: item.is_paint || false,
            is_active: true
        } as Article);
        openAliases();
    };

    const rows = filteredItems.map((item) => {
        const isExpired = item.expiry_date && dayjs(item.expiry_date).isBefore(dayjs());
        const isExpiringSoon = item.expiry_date && dayjs(item.expiry_date).diff(dayjs(), 'day') < 30 && !isExpired;
        const hasSurplus = item.surplus_qty > 0;

        let rowColor = undefined;
        if (isExpired) rowColor = 'var(--mantine-color-red-1)';
        else if (isExpiringSoon) rowColor = 'var(--mantine-color-orange-1)';

        return (
            <Table.Tr key={`${item.location_id}-${item.article_id}-${item.batch_id}`} bg={rowColor}>
                <Table.Td>
                    <Group gap="xs">
                        <Text size="sm" fw={500}>{item.article_no}</Text>
                        {hasSurplus && <Badge size="xs" color="cyan" circle>S</Badge>}
                        {isExpired && <Tooltip label="Isteklo"><IconAlertTriangle size={14} color="red" /></Tooltip>}
                    </Group>
                    <Text size="xs" c="dimmed">{item.description}</Text>
                </Table.Td>
                <Table.Td>
                    <Text size="sm">{item.manufacturer || '-'}</Text>
                </Table.Td>
                <Table.Td>
                    <Group gap="xs">
                        <Text size="sm" fw={500}>{item.batch_code}</Text>
                        {item.batch_code === 'NA' && <Badge size="xs" variant="outline" color="gray">System</Badge>}
                    </Group>
                    {item.expiry_date && (
                        <Text c={isExpired ? 'red' : (isExpiringSoon ? 'orange' : 'dimmed')} size="xs">
                            {dayjs(item.expiry_date).format('DD.MM.YYYY')}
                        </Text>
                    )}
                </Table.Td>
                <Table.Td fw={700} align="right">
                    {item.total_qty.toFixed(2)} <Text span size="xs" fw={400} c="dimmed">{item.uom || 'KG'}</Text>
                </Table.Td>
                <Table.Td align="right">
                    <Text c="dimmed" size="sm">{item.updated_at ? dayjs(item.updated_at).fromNow() : '-'}</Text>
                </Table.Td>
                {isAdmin && (
                    <Table.Td>
                        <Menu shadow="md" width={200} position="bottom-end">
                            <Menu.Target>
                                <ActionIcon variant="subtle" color="gray">
                                    <IconDotsVertical size={16} />
                                </ActionIcon>
                            </Menu.Target>

                            <Menu.Dropdown>
                                <Menu.Label>Akcije na zalihama</Menu.Label>
                                <Menu.Item
                                    leftSection={<IconPackageImport size={14} />}
                                    onClick={() => navigate('/receiving', {
                                        state: {
                                            article_id: item.article_id,
                                            article_no: item.article_no,
                                            description: item.description
                                        }
                                    })}
                                >
                                    Primi robu
                                </Menu.Item>
                                <Menu.Item
                                    leftSection={<IconClipboardCheck size={14} />}
                                    onClick={() => { setSelectedItem(item); openCountModal(); }}
                                >
                                    Popis zaliha
                                </Menu.Item>

                                <Menu.Divider />
                                <Menu.Label>Akcije na artiklu</Menu.Label>
                                <Menu.Item leftSection={<IconEdit size={14} />} onClick={() => handleEditArticle(item)}>
                                    Uredi artikl
                                </Menu.Item>
                                <Menu.Item leftSection={<IconTag size={14} />} onClick={() => handleAliases(item)}>
                                    Aliasi
                                </Menu.Item>

                                <Menu.Item
                                    leftSection={<IconArchive size={14} />}
                                    color="red"
                                    onClick={() => handleArchiveArticle(item.article_id)}
                                >
                                    Arhiviraj artikl
                                </Menu.Item>
                                {/* We can't know if it's inactive from InventoryItem yet, so Restore isn't easily shown here unless we assume filtered list implies it */}
                            </Menu.Dropdown>
                        </Menu>
                    </Table.Td>
                )}
            </Table.Tr>
        );
    });

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="lg">
                <Title order={2}>Pregled artikala</Title>
                {isAdmin && (
                    <Button leftSection={<IconPlus size={16} />} onClick={() => { setEditingArticle(null); openArticleForm(); }}>
                        Novi artikl
                    </Button>
                )}
            </Group>

            {isError && (
                <Alert icon={<IconAlertTriangle size={16} />} title="Greška pri učitavanju" color="red" mb="md">
                    <Stack gap="xs">
                        <Text size="sm">{extractErrorMessage(error)}</Text>
                        <Button variant="outline" size="xs" color="red" leftSection={<IconRefresh size={14} />} onClick={() => refetch()} style={{ width: 'fit-content' }}>
                            Pokušaj ponovo
                        </Button>
                    </Stack>
                </Alert>
            )}

            <Paper shadow="xs" p="md" withBorder>
                <Group mb="md" justify="space-between">
                    <Group style={{ flex: 1 }} gap="sm">
                        <TextInput
                            placeholder="Pretraži po artiklu, šarži..."
                            leftSection={<IconSearch size={16} />}
                            value={search}
                            onChange={(e) => setSearch(e.currentTarget.value)}
                            style={{ width: 260 }}
                        />
                        {/* P1 fix: category Select replaces Paint/Consumables tabs */}
                        <Select
                            placeholder="Sve kategorije"
                            clearable
                            data={[
                                { value: 'paint', label: 'Boje' },
                                { value: 'consumable', label: 'Potrošni materijal' },
                                { value: 'other', label: 'Ostalo' },
                            ]}
                            value={category}
                            onChange={setCategory}
                            style={{ width: 200 }}
                        />
                    </Group>
                    {/* P1 fix: state SegmentedControl */}
                    <SegmentedControl
                        value={stateFilter}
                        onChange={(v) => setStateFilter(v as 'active' | 'inactive' | 'all')}
                        data={[
                            { label: 'Aktivni', value: 'active' },
                            { label: 'Neaktivni', value: 'inactive' },
                            { label: 'Svi', value: 'all' },
                        ]}
                        size="xs"
                    />
                </Group>

                <div style={{ position: 'relative', minHeight: 200 }}>
                    <LoadingOverlay visible={isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

                    {filteredItems.length === 0 && !isLoading ? (
                        <EmptyState message="Nema stavki." />
                    ) : (
                        <Table striped highlightOnHover>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Artikl</Table.Th>
                                    <Table.Th>Proizvođač</Table.Th>
                                    <Table.Th>Šarža / Rok</Table.Th>
                                    <Table.Th style={{ textAlign: 'right' }}>Kol.</Table.Th>
                                    <Table.Th style={{ textAlign: 'right' }}>Zadnja aktivnost</Table.Th>
                                    {isAdmin && <Table.Th w={50}></Table.Th>}
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>{rows}</Table.Tbody>
                        </Table>
                    )}
                </div>
            </Paper>

            <CountModal
                item={selectedItem}
                opened={countModalOpened}
                onClose={() => { closeCountModal(); setSelectedItem(null); }}
            />

            <ArticleForm
                opened={articleFormOpened}
                onClose={() => { closeArticleForm(); setEditingArticle(null); }}
                article={editingArticle}
            />

            <AliasesEditor
                article={editingArticle}
                opened={aliasesOpened}
                onClose={() => { closeAliases(); setEditingArticle(null); }}
            />
        </Container >
    );
}
