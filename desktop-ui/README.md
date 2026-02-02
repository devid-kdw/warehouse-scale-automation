# Warehouse Desktop UI

Electron + React application for testing the Warehouse Automation Backend.

## Prerequisites

- Node.js (v18+)
- Backend running on `http://localhost:5001` (or other URL)

## Setup

1.  Navigate to this folder:
    ```bash
    cd desktop-ui
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

## Development

Run the application in development mode (Vite + Electron):

```bash
npm run electron:dev
```

## Configuration

On first launch, you will be redirected to the **Settings** page.

1.  **Base URL**: Enter your backend URL (default: `http://localhost:5001`).
2.  **API Token**: Enter the Bearer token (e.g. from `.env` or `flask seed` output).
3.  **Actor ID**: Enter the User ID to use for actions (default: `1`).

## Troublehsooting

- **Connection Failed**: Ensure backend is running and `CORS` is enabled (or Electron context isolation handles it).
- **White Screen**: Check console (Ctrl+Shift+I) for errors.
- **Validation Errors**: Ensure you selected an Article before creating a Batch, and all IDs exist.

## Project Structure

- `src/api`: Axios client, Types, and standardized Endpoints.
- `src/pages`: React components for each screen.
- `electron`: Main process code.
