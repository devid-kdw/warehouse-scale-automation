import { Center, Stack, Text, ThemeIcon } from '@mantine/core';
import { IconInbox } from '@tabler/icons-react';

interface EmptyStateProps {
    message?: string;
}

export function EmptyState({ message = 'No items found' }: EmptyStateProps) {
    return (
        <Center h={200}>
            <Stack align="center" gap="md">
                <ThemeIcon size={60} radius="xl" variant="light" color="gray">
                    <IconInbox size={32} />
                </ThemeIcon>
                <Text c="dimmed" size="lg">{message}</Text>
            </Stack>
        </Center>
    );
}
