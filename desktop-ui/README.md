# Warehouse Desktop UI

Electron + React application for the Warehouse Automation system.

## Prerequisites

- Node.js (v18+)
- Backend running on `http://localhost:5001` (or configured URL)

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

Or run just the web UI in the browser (for fast iteration):

```bash
npm run dev
# Open http://localhost:5173
```

## Configuration & Login

On first launch you will see the **Login** screen.

1.  **Backend URL**: Configured in the **Settings** page (default: `http://localhost:5001`).
2.  **Login**: Enter your **username** and **password**. The backend issues a JWT access token (15 min) and refresh token (7 days).
3.  **Roles**: The JWT `role` claim controls what you see:
    -   **OPERATOR**: Draft Entry + Inventory view (read-only).
    -   **ADMIN**: Full access — Drafts, Approvals, Inventory, Receiving, Articles, Batches, Reports.

No manual API tokens or actor IDs are needed — authentication is handled automatically via JWT.

## Troubleshooting

- **Connection Failed**: Ensure backend is running and reachable. Check Settings page for correct URL.
- **White Screen**: Open DevTools (Ctrl+Shift+I / Cmd+Option+I) and check console for errors.
- **401 Redirect Loop**: Token may have expired. Log out and log back in.
- **Validation Errors**: Ensure you selected an Article before creating a Batch, and all IDs exist.

## Project Structure

- `src/api`: Axios client, Types, Endpoints, and Service functions.
- `src/pages`: React page components for each screen.
- `src/components`: Shared UI components (Sidebar, ErrorBoundary, etc.).
- `src/hooks`: Custom React hooks (`useAuth`).
- `electron`: Electron main process code.
