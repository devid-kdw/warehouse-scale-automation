import { Alert } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

interface ErrorAlertProps {
    title?: string;
    message: string;
}

export function ErrorAlert({ title = 'Error', message }: ErrorAlertProps) {
    return (
        <Alert icon={<IconAlertCircle size="1rem" />} title={title} color="red" variant="filled">
            {message}
        </Alert>
    );
}
