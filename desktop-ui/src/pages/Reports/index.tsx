
import { useState } from 'react';
import { Container, Tabs, Paper, Title } from '@mantine/core';
import { IconListCheck, IconClipboardList, IconChartDots } from '@tabler/icons-react';
import { InventurnaLista } from './InventurnaLista';
import { SurplusLista } from './SurplusLista';
import { Statistike } from './Statistike';

export default function Reports() {
    const [activeTab, setActiveTab] = useState<string | null>('inventurna');

    return (
        <Container size="xl" py="xl">
            <Title order={2} mb="lg">Izvještaji</Title>

            <Paper shadow="xs" p="md" withBorder>
                <Tabs value={activeTab} onChange={setActiveTab} variant="outline">
                    <Tabs.List mb="md">
                        <Tabs.Tab value="inventurna" leftSection={<IconClipboardList size={16} />}>
                            Inventurna Lista
                        </Tabs.Tab>
                        <Tabs.Tab value="surplus" leftSection={<IconListCheck size={16} />}>
                            Surplus Lista
                        </Tabs.Tab>
                        <Tabs.Tab value="stats" leftSection={<IconChartDots size={16} />}>
                            Statistike
                        </Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="inventurna" pt="xs">
                        <InventurnaLista />
                    </Tabs.Panel>

                    <Tabs.Panel value="surplus" pt="xs">
                        <SurplusLista />
                    </Tabs.Panel>

                    <Tabs.Panel value="stats" pt="xs">
                        <Statistike />
                    </Tabs.Panel>
                </Tabs>
            </Paper>
        </Container>
    );
}
