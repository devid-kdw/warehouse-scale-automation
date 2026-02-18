
import { SimpleGrid, Paper, Text, Group, ThemeIcon, Table, LoadingOverlay, Title, Badge } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { IconChartBar, IconAlertTriangle, IconArrowUpRight } from '@tabler/icons-react';
import { getStatistics } from '../../api/services';

function StatCard({ title, value, icon, color }: { title: string, value: string | number, icon: any, color: string }) {
    return (
        <Paper withBorder p="md" radius="md">
            <Group justify="space-between">
                <div>
                    <Text c="dimmed" tt="uppercase" fw={700} fz="xs">
                        {title}
                    </Text>
                    <Text fw={700} fz="xl">
                        {value}
                    </Text>
                </div>
                <ThemeIcon color={color} variant="light" size={38} radius="md">
                    {icon}
                </ThemeIcon>
            </Group>
        </Paper>
    );
}

const RISK_COLORS: Record<string, string> = {
    RED: 'red',
    YELLOW: 'yellow',
    GREEN: 'green',
};

export function Statistike() {
    // P1 fix: backend returns {items: [...], total: N} for all statistics endpoints
    const { data: consumptionData, isLoading: loadingConsumption } = useQuery({
        queryKey: ['stats', 'consumption'],
        queryFn: () => getStatistics('consumption')
    });

    const { data: risksData, isLoading: loadingRisks } = useQuery({
        queryKey: ['stats', 'risks'],
        queryFn: () => getStatistics('reorder-risk')
    });

    const { data: topData, isLoading: loadingTop } = useQuery({
        queryKey: ['stats', 'top-consumers'],
        queryFn: () => getStatistics('top-consumers')
    });

    // P1 fix: backend returns {items: ConsumptionStatsSchema[], total: N}
    const consumptionItems: any[] = consumptionData?.items || [];
    const reorderRisks: any[] = risksData?.items || [];
    // P1 fix: top-consumers returns flat array (many=True), not {items: [...]}
    const topConsumers: any[] = Array.isArray(topData) ? topData : (topData?.items || []);

    const totalConsumed = consumptionItems.reduce((sum: number, item: any) => sum + (item.quantity || 0), 0);
    const redRisks = reorderRisks.filter((r: any) => r.risk_level === 'RED').length;

    return (
        <div>
            <SimpleGrid cols={{ base: 1, sm: 3 }} mb="xl">
                <StatCard
                    title="Ukupna potrošnja (30d)"
                    value={totalConsumed > 0 ? `${totalConsumed.toFixed(2)}` : '-'}
                    icon={<IconChartBar size={28} />}
                    color="blue"
                />
                <StatCard
                    title="Kritični reorder (RED)"
                    value={redRisks}
                    icon={<IconAlertTriangle size={28} />}
                    color="red"
                />
                <StatCard
                    title="Ukupno artikala za reorder"
                    value={reorderRisks.length}
                    icon={<IconArrowUpRight size={28} />}
                    color="teal"
                />
            </SimpleGrid>

            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
                <Paper withBorder p="md" radius="md" h={400}>
                    <Title order={4} mb="md">Top potrošači</Title>
                    <div style={{ position: 'relative', height: 320, overflow: 'auto' }}>
                        <LoadingOverlay visible={loadingTop || loadingConsumption} />
                        <Table striped>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Artikal</Table.Th>
                                    <Table.Th ta="right">Količina</Table.Th>
                                    <Table.Th ta="right">UOM</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {topConsumers.map((item: any, i: number) => (
                                    <Table.Tr key={i}>
                                        <Table.Td>{item.article_no} — {item.description}</Table.Td>
                                        {/* P1 fix: backend field is 'quantity' not 'quantity_kg' */}
                                        <Table.Td ta="right">{item.quantity?.toFixed(2) ?? '-'}</Table.Td>
                                        <Table.Td ta="right">{item.uom || '-'}</Table.Td>
                                    </Table.Tr>
                                ))}
                                {!loadingTop && topConsumers.length === 0 && (
                                    <Table.Tr>
                                        <Table.Td colSpan={3}>
                                            <Text ta="center" c="dimmed" py="md">Nema podataka.</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                )}
                            </Table.Tbody>
                        </Table>
                    </div>
                </Paper>

                <Paper withBorder p="md" radius="md" h={400}>
                    <Title order={4} mb="md" c="red">Upozorenja za reorder</Title>
                    <div style={{ position: 'relative', height: 320, overflow: 'auto' }}>
                        <LoadingOverlay visible={loadingRisks} />
                        <Table striped>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Artikal</Table.Th>
                                    {/* P1 fix: backend fields are 'stock' and 'threshold', not 'total_qty'/'reorder_threshold' */}
                                    <Table.Th ta="right">Zaliha</Table.Th>
                                    <Table.Th ta="right">Prag</Table.Th>
                                    <Table.Th>Rizik</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {reorderRisks.map((item: any, i: number) => (
                                    <Table.Tr key={i}>
                                        <Table.Td>{item.article_no}</Table.Td>
                                        <Table.Td ta="right" c="red" fw={700}>{item.stock?.toFixed(2) ?? '-'}</Table.Td>
                                        <Table.Td ta="right">{item.threshold?.toFixed(2) ?? '-'}</Table.Td>
                                        <Table.Td>
                                            <Badge color={RISK_COLORS[item.risk_level] || 'gray'} size="sm">
                                                {item.risk_level}
                                            </Badge>
                                        </Table.Td>
                                    </Table.Tr>
                                ))}
                                {!loadingRisks && reorderRisks.length === 0 && (
                                    <Table.Tr>
                                        <Table.Td colSpan={4}>
                                            <Text ta="center" c="dimmed" py="md">Nema upozorenja.</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                )}
                            </Table.Tbody>
                        </Table>
                    </div>
                </Paper>
            </SimpleGrid>
        </div>
    );
}
