import {
    Modal, Button, TextInput, Group, Table, ActionIcon,
    LoadingOverlay, Text, Alert
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { IconTrash, IconPlus, IconCheck } from '@tabler/icons-react';
import { getAliases, createAlias, deleteAlias, extractErrorMessage } from '../../../api/services';
import { Article } from '../../../api/types';

interface AliasesEditorProps {
    article: Article | null;
    opened: boolean;
    onClose: () => void;
}

export function AliasesEditor({ article, opened, onClose }: AliasesEditorProps) {
    const queryClient = useQueryClient();

    // Fetch Aliases
    const { data, isLoading } = useQuery({
        queryKey: ['aliases', article?.id],
        queryFn: () => getAliases(article!.id),
        enabled: !!article,
    });

    const aliases = data?.items || [];
    const isLimitReached = aliases.length >= 5;

    // Create Mutation
    const createMutation = useMutation({
        mutationFn: (alias: string) => createAlias(article!.id, alias),
        onSuccess: () => {
            notifications.show({ title: 'Success', message: 'Alias added successfully', color: 'green', icon: <IconCheck size={16} /> });
            queryClient.invalidateQueries({ queryKey: ['aliases', article?.id] });
            form.reset();
        },
        onError: (err) => {
            notifications.show({ title: 'Failed to add alias', message: extractErrorMessage(err), color: 'red' });
        }
    });

    // Delete Mutation
    const deleteMutation = useMutation({
        mutationFn: (aliasId: number) => deleteAlias(article!.id, aliasId),
        onSuccess: () => {
            notifications.show({ title: 'Success', message: 'Alias removed successfully', color: 'green', icon: <IconCheck size={16} /> });
            queryClient.invalidateQueries({ queryKey: ['aliases', article?.id] });
        },
        onError: (err) => {
            notifications.show({ title: 'Failed to remove alias', message: extractErrorMessage(err), color: 'red' });
        }
    });

    const form = useForm({
        initialValues: { alias: '' },
        validate: {
            alias: (val) => val.trim().length < 2 ? 'Alias too short' : null,
        },
    });

    const handleSubmit = (values: typeof form.values) => {
        createMutation.mutate(values.alias);
    };

    return (
        <Modal opened={opened} onClose={onClose} title={`Aliases: ${article?.article_no}`} centered>
            <LoadingOverlay visible={isLoading} />

            <Text size="sm" c="dimmed" mb="md">
                Manage alternative names/codes for this article. Max 5 aliases.
            </Text>

            {/* List */}
            <Table mb="md" withTableBorder>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th>Alias</Table.Th>
                        <Table.Th w={50}></Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                    {aliases.length === 0 ? (
                        <Table.Tr>
                            <Table.Td colSpan={2} align="center" c="dimmed">No aliases defined</Table.Td>
                        </Table.Tr>
                    ) : (
                        aliases.map(a => (
                            <Table.Tr key={a.id}>
                                <Table.Td>{a.alias}</Table.Td>
                                <Table.Td>
                                    <ActionIcon
                                        color="red" variant="subtle"
                                        onClick={() => deleteMutation.mutate(a.id)}
                                        loading={deleteMutation.isPending}
                                    >
                                        <IconTrash size={16} />
                                    </ActionIcon>
                                </Table.Td>
                            </Table.Tr>
                        ))
                    )}
                </Table.Tbody>
            </Table>

            {/* Add Form */}
            {isLimitReached ? (
                <Alert color="orange" title="Limit Reached">
                    Maximum of 5 aliases allowed per article.
                </Alert>
            ) : (
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <Group align="flex-start" gap="xs">
                        <TextInput
                            placeholder="Enter new alias"
                            style={{ flex: 1 }}
                            {...form.getInputProps('alias')}
                        />
                        <Button
                            type="submit"
                            variant="filled"
                            disabled={!form.isValid()}
                            loading={createMutation.isPending}
                        >
                            <IconPlus size={16} />
                        </Button>
                    </Group>
                </form>
            )}

            <Group justify="flex-end" mt="xl">
                <Button variant="default" onClick={onClose}>Close</Button>
            </Group>
        </Modal>
    );
}
