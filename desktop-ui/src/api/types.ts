// Basic Types
export interface Article {
    id: number;
    article_no: string;
    description: string;
    // V1.2 Enhanced Fields
    uom?: string; // Changed from 'KG' | 'L' to string for backend compat
    manufacturer?: string;
    manufacturer_art_number?: string;
    reorder_threshold?: number;
    is_paint: boolean;
    is_active: boolean; // Added in Phase 4
    aliases?: string[]; // Optional array of alias codes
}

/** Matches backend MissingArticleReportSchema */
export interface MissingItemReport {
    id: number;
    reported_by_user_id: number;
    location_id: number;
    raw_input: string;          // P0 fix: was 'query', backend uses 'raw_input'
    status: 'OPEN' | 'PENDING' | 'IN_REVIEW' | 'RESOLVED' | 'CLOSED' | 'REJECTED';
    resolved_article_id?: number | null;
    admin_note?: string | null; // P0 fix: was 'resolution_note'
    created_at: string;
    resolved_at?: string | null;
}

/** Matches backend AdminReportUpdateSchema */
export interface AdminReportUpdatePayload {
    status: 'IN_REVIEW' | 'RESOLVED' | 'CLOSED' | 'REJECTED';
    admin_note?: string | null;
    resolved_article_id?: number | null;
}

/** @deprecated Use AdminReportUpdatePayload */
export interface ResolveReportPayload {
    action: 'ignore' | 'alias' | 'create';
    alias_for_article_id?: number;
    new_article_data?: Partial<Article>;
    note?: string;
}

/** Matches backend DailyApprovalSummarySchema */
export interface DailyApprovalSummary {
    date: string;
    location_id: number;
    total_lines: number;
    total_qty: number;
}

/** Matches backend DailyApprovalDetailSchema */
export interface DailyApprovalDetail {
    article_id: number;
    article_no: string;
    article_name: string;
    batch_id: number;
    batch_code: string;
    location_id: number;
    total_qty: number;
    uom: string;
    draft_ids: number[];
}

export interface Alias {
    id: number;
    article_id: number;
    alias: string;
    created_at: string;
}

export interface Batch {
    id: number;
    article_id: number;
    batch_code: string;
    is_active: boolean;
    expiry_date?: string; // V1.2
    created_at: string;
}

export interface WeighInDraft {
    id: number;
    location_id: number;
    article_id: number;
    batch_id: number;
    quantity_kg: number;
    status: 'DRAFT' | 'APPROVED' | 'REJECTED';
    source: string;
    created_by_user_id?: number | null;
    draft_group_id: number; // Mandatory for TASK-0001+
    client_event_id: string;
    note?: string;
    created_at: string;
}

export interface DraftGroup {
    id: number;
    name: string;
    status: 'DRAFT' | 'APPROVED' | 'REJECTED';
    source: string;
    location_id: number;
    created_at: string;
    created_by_user_id: number;
    line_count?: number;
    total_quantity_kg?: number;
    drafts?: WeighInDraft[];  // Backend returns "drafts"
    lines?: WeighInDraft[];   // Legacy alias — prefer drafts
}

export interface DraftGroupSummary {
    id: number;
    name: string;
    status: 'DRAFT' | 'APPROVED' | 'REJECTED';
    source: string;
    line_count: number;
    total_quantity_kg: number;
    created_at: string;
    created_by_name?: string;
}

export interface InventoryItem {
    location_id: number;
    location_code: string;
    article_id: number;
    article_no: string;
    description?: string;
    is_paint?: boolean;
    uom?: string; // Phase 4
    manufacturer?: string; // Phase 4
    batch_id: number;
    batch_code: string;
    expiry_date?: string;
    stock_qty: number;
    surplus_qty: number;
    total_qty: number;
    updated_at?: string;
}

export interface Transaction {
    id: number;
    tx_type: string;
    occurred_at: string;
    location_id: number;
    article_id: number;
    batch_id: number;
    quantity_kg: number;
    user_id?: number;
    source: string;
    // Denormalized
    article_no?: string;
    batch_code?: string;
    location_code?: string;
}

// API Responses
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
}

export interface ArticlesResponse extends PaginatedResponse<Article> { }
export interface DraftsResponse extends PaginatedResponse<WeighInDraft> { }
export interface BatchesResponse extends PaginatedResponse<Batch> { }
export interface AliasesResponse extends PaginatedResponse<Alias> { }
export interface InventoryResponse extends PaginatedResponse<InventoryItem> { }
export interface TransactionsResponse extends PaginatedResponse<Transaction> { }

// API Payloads
export interface CreateArticlePayload {
    article_no: string;
    description: string;
    is_paint: boolean;
    is_active: boolean;
    // V1.2
    uom?: 'KG' | 'L';
    manufacturer?: string;
    manufacturer_art_number?: string;
    reorder_threshold?: number;
}

export interface CreateBatchPayload {
    article_id: number;
    batch_code: string;
    expiry_date?: string; // YYYY-MM-DD
}

export interface CreateDraftPayload {
    location_id: number;
    article_id: number;
    batch_id: number | null;
    quantity: number; // Phase 3
    uom?: string; // Phase 3
    client_event_id: string;
    source?: string;
}

export interface ApprovalPayload {
    note?: string;
}

export interface ApprovalResponse {
    message: string;
    draft_id: number;
    new_status: string;
    consumed_surplus?: number;
    consumed_stock?: number;
    action?: any;
}

export interface ApiErrorResponse {
    error: {
        code: string;
        message: string;
        details?: Record<string, any>;
    };
}

export interface InventoryCountPayload {
    location_id?: number;
    article_id: number;
    batch_id: number;
    counted_total_qty: number;
    note?: string;
    client_event_id?: string;
}

export interface StockReceivePayload {
    location_id?: number; // Defaults to 13
    article_id: number;
    delivery_note_number: string; // Required Phase 2
    order_line_id?: number; // Optional Phase 2
    quantity: number; // Phase 2: quantity instead of quantity_kg
    uom: string; // Phase 2: KG or L
    batch_code?: string; // Optional (conditional)
    expiry_date?: string; // Optional (conditional)
    note?: string; // Conditional
    // Deprecated fields kept for compat if needed, but new flow uses above
    quantity_kg?: number;
    order_number?: string;
}

export interface ReceiptHistoryLine {
    article_no: string;
    description: string;
    batch_code: string;
    quantity_kg: number; // Legacy field
    quantity: number;    // Phase 2 field
    uom: string;         // Phase 2 field
    user_name?: string;
}

export interface ReceiptHistoryGroup {
    receipt_key: string;
    delivery_note_number?: string; // Phase 2
    order_number?: string;
    received_at: string;
    lines: ReceiptHistoryLine[];
}

export interface ReceiptHistoryResponse {
    history: ReceiptHistoryGroup[];
    total: number;
}

export interface StockReceiveResponse {
    batch_id: number;
    batch_created: boolean;
    previous_stock: string;
    new_stock: string;
    quantity_received: string;
    transaction: any;
}

export interface CreateDraftGroupPayload {
    location_id?: number; // Defaults to 13 on backend
    name?: string;
    description?: string; // Phase 3
    lines: Array<{
        article_id: number;
        batch_id: number | null;
        quantity: number; // Phase 3
        uom?: string; // Phase 3
        note?: string;
        client_event_id: string;
    }>;
}

export interface TransactionQueryParams {
    tx_type?: string;
    from?: string;   // ISO datetime
    to?: string;     // ISO datetime
    article_id?: number;
    batch_id?: number;
    location_id?: number;
    limit?: number;
    offset?: number;
}
