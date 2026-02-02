import { Container, Title, Text, Alert } from '@mantine/core';

export const DraftEntry = () => (
    <Container>
        <Title>Draft Entry</Title>
        <Text>Form coming soon...</Text>
    </Container>
);

export const DraftApproval = () => (
    <Container>
        <Title>Draft Approval</Title>
        <Text>Dashboard coming soon...</Text>
    </Container>
);

export const Articles = () => (
    <Container>
        <Title>Articles</Title>
        <Text>List coming soon...</Text>
    </Container>
);

export const Batches = () => (
    <Container>
        <Title>Batches</Title>
        <Text>List coming soon...</Text>
    </Container>
);

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
