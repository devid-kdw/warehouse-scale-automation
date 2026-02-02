import { Container, Title, Alert } from '@mantine/core';

export const Inventory = () => (
    <Container p="xl">
        <Title mb="md">Inventory</Title>
        <Alert color="orange" title="Not Available">
            Inventory listing endpoint not available in backend.
            <br />
            Please check the backend Swagger for available endpoints.
        </Alert>
    </Container>
);
