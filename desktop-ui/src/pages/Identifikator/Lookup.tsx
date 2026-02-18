
import { useState } from 'react';
import { Container, TextInput, Button, Title, Paper, Table, Text, Group, Modal, Stack, Textarea, LoadingOverlay, Alert, Badge } from '@mantine/core';
import { useMutation, useQuery } from '@tanstack/react-query';
import { IconSearch, IconAlertCircle, IconCheck, IconFileReport } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { lookupArticle, reportMissingItem, extractErrorMessage } from '../../api/services';
import { Article } from '../../api/types';

export function IdentifikatorLookup() {
    const [query, setQuery] = useState('');
    const [searchedQuery, setSearchedQuery] = useState('');
    const [reportModalOpen, setReportModalOpen] = useState(false);
    const [reportNote, setReportNote] = useState('');

    // P0 fix: backend returns single article or 404 (not array)
    const { data: result, isLoading, isError, error } = useQuery<Article | null>({
        queryKey: ['identifikator', 'lookup', searchedQuery],
        queryFn: () => lookupArticle(searchedQuery),
        enabled: searchedQuery.length > 0
    });

    const handleSearch = () => {
        if (query.trim().length > 0) {
            setSearchedQuery(query.trim());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch();
    };

    // P0 fix: payload is {raw_input, location_id}
    const reportMutation = useMutation({
        mutationFn: () => reportMissingItem(searchedQuery, 13),
        onSuccess: () => {
            notifications.show({ title: 'Prijava poslana', message: 'Administrator je obaviješten.', color: 'green', icon: <IconCheck size={16} /> });
            setReportModalOpen(false);
            setReportNote('');
        },
        onError: (err) => {
            notifications.show({ title: 'Greška', message: extractErrorMessage(err), color: 'red', icon: <IconAlertCircle size={16} /> });
        }
    });

    const hasSearched = searchedQuery.length > 0;
    const notFound = hasSearched && !isLoading && !isError && result === null;

    return (
        <Container size="md" py="xl">
            <Title order={2} mb="lg" ta="center">Pretraga artikla</Title>

            <Paper withBorder p="lg" shadow="sm" radius="md">
                <Group align="flex-end">
                    <TextInput
                        label="Pretraži artikal"
                        placeholder="Unesite šifru, naziv ili alias..."
                        value={query}
                        onChange={(e) => setQuery(e.currentTarget.value)}
                        onKeyDown={handleKeyDown}
                        leftSection={<IconSearch size={16} />}
                        style={{ flex: 1 }}
                    />
                    <Button onClick={handleSearch} loading={isLoading}>Pretraži</Button>
                </Group>
            </Paper>

            <div style={{ marginTop: 20, position: 'relative', minHeight: 100 }}>
                <LoadingOverlay visible={isLoading} overlayProps={{ blur: 2 }} />

                {isError && (
                    <Alert color="red" icon={<IconAlertCircle size={16} />} title="Greška">
                        {extractErrorMessage(error)}
                    </Alert>
                )}

                {result && (
                    <Paper withBorder mt="md" p="md">
                        <Title order={4} mb="md">Rezultat za "{searchedQuery}"</Title>
                        <Table striped>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Šifra artikla</Table.Th>
                                    <Table.Th>Naziv</Table.Th>
                                    <Table.Th>UOM</Table.Th>
                                    <Table.Th>Status</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                <Table.Tr>
                                    <Table.Td fw={700}>{result.article_no}</Table.Td>
                                    <Table.Td>{result.description}</Table.Td>
                                    <Table.Td>{result.uom || '-'}</Table.Td>
                                    <Table.Td>
                                        <Badge color={result.is_active ? 'green' : 'gray'}>
                                            {result.is_active ? 'Aktivan' : 'Neaktivan'}
                                        </Badge>
                                    </Table.Td>
                                </Table.Tr>
                            </Table.Tbody>
                        </Table>
                    </Paper>
                )}

                {notFound && (
                    <Alert color="yellow" title="Artikal nije pronađen" icon={<IconAlertCircle size={16} />} mt="md">
                        Nije pronađen artikal za "<b>{searchedQuery}</b>".
                        <br />
                        <Button
                            variant="light"
                            color="orange"
                            mt="sm"
                            leftSection={<IconFileReport size={16} />}
                            onClick={() => setReportModalOpen(true)}
                        >
                            Prijavi nedostajući artikal
                        </Button>
                    </Alert>
                )}
            </div>

            <Modal opened={reportModalOpen} onClose={() => setReportModalOpen(false)} title="Prijava nedostajućeg artikla">
                <Stack>
                    <Text size="sm">
                        Prijavljujete "<b>{searchedQuery}</b>" kao nedostajući artikal. Administrator će pregledati prijavu.
                    </Text>
                    <Textarea
                        label="Napomena (opcionalno)"
                        placeholder="npr. Plava boja u kanti..."
                        value={reportNote}
                        onChange={(e) => setReportNote(e.currentTarget.value)}
                    />
                    <Group justify="flex-end">
                        <Button variant="default" onClick={() => setReportModalOpen(false)}>Odustani</Button>
                        <Button
                            loading={reportMutation.isPending}
                            color="orange"
                            onClick={() => reportMutation.mutate()}
                        >
                            Pošalji prijavu
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Container>
    );
}
