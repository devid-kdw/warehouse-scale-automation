
import { useEffect } from 'react';
import {
    Modal, TextInput, Checkbox, Group, Button, Stack, Select, NumberInput, LoadingOverlay, Alert
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';
import { createArticle, updateArticle, extractErrorMessage } from '../../../api/services';
import { Article } from '../../../api/types';

interface ArticleFormProps {
    opened: boolean;
    onClose: () => void;
    article?: Article | null; // If provided, we are in Edit mode
}

export function ArticleForm({ opened, onClose, article }: ArticleFormProps) {
    const queryClient = useQueryClient();
    const isEdit = !!article;

    const form = useForm({
        initialValues: {
            article_no: '',
            description: '',
            uom: 'KG',
            manufacturer: '',
            manufacturer_art_number: '',
            reorder_threshold: 0,
            is_paint: false,
            is_active: true,
        },
        validate: {
            article_no: (val) => val.trim().length < 1 ? 'Article Number is required' : null,
            description: (val) => val.trim().length < 1 ? 'Description is required' : null,
        },
    });

    // Populate form when editing
    useEffect(() => {
        if (article) {
            form.setValues({
                article_no: article.article_no,
                description: article.description,
                uom: article.uom || 'KG',
                manufacturer: article.manufacturer || '',
                manufacturer_art_number: article.manufacturer_art_number || '',
                reorder_threshold: article.reorder_threshold || 0,
                is_paint: article.is_paint,
                is_active: article.is_active,
            });
        } else {
            form.reset();
        }
    }, [article, opened]);

    const mutation = useMutation({
        mutationFn: async (values: typeof form.values) => {
            const payload = {
                ...values,
                uom: values.uom as 'KG' | 'L'
            };
            if (isEdit && article) {
                return updateArticle(article.id, payload);
            } else {
                return createArticle(payload);
            }
        },
        onSuccess: () => {
            notifications.show({
                title: 'Success',
                message: isEdit ? 'Article updated' : 'Article created',
                color: 'green',
                icon: <IconCheck size={16} />
            });
            queryClient.invalidateQueries({ queryKey: ['inventory'] }); // Invalidate inventory
            queryClient.invalidateQueries({ queryKey: ['articles'] });
            onClose();
            form.reset();
        },
        onError: (err) => {
            notifications.show({
                title: 'Error',
                message: extractErrorMessage(err),
                color: 'red',
                icon: <IconX size={16} />
            });
        }
    });

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title={isEdit ? `Edit Article: ${article?.article_no}` : "Create New Article"}
            centered
        >
            <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                <Stack>
                    <LoadingOverlay visible={mutation.isPending} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />

                    {mutation.isError && (
                        <Alert color="red" icon={<IconAlertCircle size={16} />}>
                            {extractErrorMessage(mutation.error)}
                        </Alert>
                    )}

                    <TextInput
                        label="Šifra artikla"
                        placeholder="npr. 100-200"
                        withAsterisk
                        disabled={isEdit}
                        {...form.getInputProps('article_no')}
                    />

                    <TextInput
                        label="Naziv"
                        placeholder="Naziv artikla"
                        withAsterisk
                        {...form.getInputProps('description')}
                    />

                    <Group grow>
                        <Select
                            label="JM"
                            data={['KG', 'L']}
                            {...form.getInputProps('uom')}
                        />
                        <NumberInput
                            label="Prag narudžbe"
                            min={0}
                            {...form.getInputProps('reorder_threshold')}
                        />
                    </Group>

                    <TextInput
                        label="Proizvođač"
                        {...form.getInputProps('manufacturer')}
                    />

                    <TextInput
                        label="Art. br. proizvođača"
                        {...form.getInputProps('manufacturer_art_number')}
                    />

                    <Checkbox
                        label="Je li boja?"
                        description="Označi ako je artikl boja"
                        mt="xs"
                        {...form.getInputProps('is_paint', { type: 'checkbox' })}
                    />

                    <Checkbox
                        label="Aktivan"
                        description="Odznaka za arhiviranje"
                        mt="xs"
                        {...form.getInputProps('is_active', { type: 'checkbox' })}
                    />

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={onClose}>Odustani</Button>
                        <Button type="submit" loading={mutation.isPending}>
                            {isEdit ? 'Spremi' : 'Kreiraj'}
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
}
