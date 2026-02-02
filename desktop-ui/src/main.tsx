import * as React from 'react';
import * as ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import App from './App';
import '@mantine/core/styles.css';

import { theme } from './theme';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <MantineProvider theme={theme}>
            <App />
        </MantineProvider>
    </React.StrictMode>
);
