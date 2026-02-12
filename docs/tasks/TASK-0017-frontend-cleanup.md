# Task Brief: TASK-0017 — Frontend Cleanup & Improvements

**Created**: 2026-02-10  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0-Critical (BUG-4 frontend), P2-Medium (rest)  
**Source**: [Orchestrator Review](../status/ORCHESTRATOR_REVIEW_2026-02-10.md)

---

## 🎯 Goal

Fix location_id defaults, remove debug artifacts, fix type inconsistencies, and add missing UI features identified during orchestrator review.

---

## 📋 Scope

### In Scope
- [BUG-4-FE] **Change all hardcoded `location_id: 1` to `location_id: 13`**
- [BUG-5] Remove `console.log` debug statements from API client
- [INC-2] Add `location_id` to `CreateDraftGroupPayload` and BulkDraftEntry
- [IMP-6] Add "Received By" column to Receipt History table
- [IMP-7] Add React Error Boundary component around App

### Out of Scope
- IMP-5 (Operator inventory access) — requires separate DECISION
- Major UI redesigns
- New page features

---

## 🔧 Technical Changes

### 1. Fix Location ID Defaults — P0 CRITICAL

> [!CAUTION]
> Per RULES_OF_ENGAGEMENT.md Rule 3 and Stefan's explicit confirmation: **Default Location ID = 13.** All `location_id: 1` must become `location_id: 13`.

#### `src/pages/Receiving/index.tsx` (line 28)
```diff
         // Hidden fields
-        location_id: 1 // Default to 1
+        location_id: 13 // Default location (warehouse 13)
```

#### `src/pages/Drafts/DraftEntry.tsx` (line 42)
```diff
-        location_id: '1',
+        location_id: '13',
```

#### `src/api/types.ts` (line 175)
```diff
-    location_id?: number; // Defaults to 1
+    location_id?: number; // Defaults to 13
```

---

### 2. Remove Debug Logs — `src/api/client.ts`

**Problem:** Lines 61 and 65 contain `console.log` that leak auth info to browser console.

**Fix:** Either delete both lines, or gate behind env check:
```diff
-console.log('[API Client] Request to:', config.url, 'Token present:', !!token, 'isPublic:', isPublicEndpoint);
+if (import.meta.env.DEV) {
+    console.debug('[API Client]', config.method?.toUpperCase(), config.url);
+}

-console.log('[API Client] Added Authorization header');
 // Remove entirely - no value in production or dev
```

---

### 3. Fix `CreateDraftGroupPayload` — `src/api/types.ts`

**Problem:** Missing `location_id` field. Backend `DraftGroupCreateSchema` requires it.

**Fix:**
```diff
 export interface CreateDraftGroupPayload {
+    location_id?: number; // Defaults to 13 on backend
     name?: string;
     lines: Array<{
```

And in `BulkDraftEntry.tsx`, add `location_id: 13` to the mutation payload:
```diff
 return createDraftGroup({
+    location_id: 13,
     name: values.name || undefined,
     lines: values.lines.map(l => ({
```

---

### 4. Add "Received By" Column — `src/pages/Inventory/ReceiptHistory.tsx`

The backend already sends `user_name` in each receipt line. Add a column:

```diff
 <Table.Thead>
     <Table.Tr>
         <Table.Th>Article</Table.Th>
         <Table.Th>Description</Table.Th>
         <Table.Th>Batch</Table.Th>
+        <Table.Th>Received By</Table.Th>
         <Table.Th align="right">Qty (kg)</Table.Th>
     </Table.Tr>
 </Table.Thead>

 {group.lines.map((line, idx) => (
     <Table.Tr key={...}>
         <Table.Td>{line.article_no}</Table.Td>
         <Table.Td>{line.description}</Table.Td>
         <Table.Td>...</Table.Td>
+        <Table.Td>{line.user_name}</Table.Td>
         <Table.Td fw={700} align="right">{line.quantity_kg.toFixed(2)}</Table.Td>
     </Table.Tr>
 ))}
```

Also update `ReceiptHistoryLine` type in `types.ts`:
```diff
 export interface ReceiptHistoryLine {
     article_no: string;
     description: string;
     batch_code: string;
     quantity_kg: number;
+    user_name?: string;
 }
```

---

### 5. Add Error Boundary — `src/components/ErrorBoundary.tsx` [NEW]

Create a basic React Error Boundary:

```tsx
import { Component, ReactNode } from 'react';
import { Container, Title, Text, Button, Stack, Paper } from '@mantine/core';
import { IconAlertTriangle } from '@tabler/icons-react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error?: Error; }

export class ErrorBoundary extends Component<Props, State> {
    state: State = { hasError: false };

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    render() {
        if (this.state.hasError) {
            return (
                <Container size="sm" py="xl">
                    <Paper shadow="sm" p="xl" withBorder>
                        <Stack align="center">
                            <IconAlertTriangle size={48} color="red" />
                            <Title order={3}>Something went wrong</Title>
                            <Text c="dimmed">{this.state.error?.message}</Text>
                            <Button onClick={() => window.location.reload()}>
                                Reload Application
                            </Button>
                        </Stack>
                    </Paper>
                </Container>
            );
        }
        return this.props.children;
    }
}
```

Wrap in `App.tsx`:
```diff
+import { ErrorBoundary } from './components/ErrorBoundary';

 function App() {
     return (
+        <ErrorBoundary>
         <QueryClientProvider client={queryClient}>
             <HashRouter>
                 <Routes>
                     <Route path="/login" element={<Login />} />
                     <Route path="/*" element={<Layout />} />
                 </Routes>
             </HashRouter>
         </QueryClientProvider>
+        </ErrorBoundary>
     );
 }
```

---

## ✅ Acceptance Criteria

1. [ ] **All `location_id` defaults are `13`** (Receiving, DraftEntry, BulkDraftEntry, types)
2. [ ] No `console.log` in `client.ts` (or gated behind DEV only)
3. [ ] `CreateDraftGroupPayload` includes `location_id`
4. [ ] Bulk Draft Entry sends `location_id: 13` in payload
5. [ ] Receipt History shows "Received By" column
6. [ ] Error Boundary catches and displays component crashes
7. [ ] Build passes: `npm run build` exits 0
8. [ ] No new TypeScript errors

---

## 🧪 Test Plan

### Manual Testing
1. Open browser console → No `[API Client]` logs in production build
2. Create a Bulk Draft Group → Confirm it succeeds (no 400 error)
3. Navigate to Receipt History → Confirm "Received By" column displays
4. Temporarily throw `Error` in a component → Confirm Error Boundary renders
5. Create a Draft → Verify `location_id=13` in network request payload

### Automated
```bash
cd desktop-ui && npm run build
```

---

## 📚 Related Documentation

- [Orchestrator Review](../status/ORCHESTRATOR_REVIEW_2026-02-10.md)
- [RULES_OF_ENGAGEMENT.md](../team/RULES_OF_ENGAGEMENT.md) — Location ID = 13
- [AGENTS.md](../team/AGENTS.md) — Frontend Agent permissions
- [CHANGELOG.md](../team/CHANGELOG.md) — Must update after fixes

---

**Status Updates**:
- 2026-02-10: Task created from Orchestrator Review
