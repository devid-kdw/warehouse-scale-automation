// Basic Types
export interface Article {
    id: number;
    article_no: string;
    description: string;
    is_paint: boolean;
    is_active: boolean;
    // V1.2 Enhanced Fields
    uom?: 'KG' | 'L';
    manufacturer?: string;
    manufacturer_art_number?: string;
    reorder_threshold?: number;
    created_at?: string;
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
    client_event_id: string;
    note?: string;
    created_at: string;
}

export interface InventoryItem {
    location_id: number;
    location_code: string;
    article_id: number;
    article_no: string;
    description?: string;
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
    batch_id: number;
    quantity_kg: number;
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
    consumed_surplus_kg?: number;
    consumed_stock_kg?: number;
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
    location_id?: number; // Defaults to 1
    article_id: number;
    batch_code: string;
    quantity_kg: number;
    expiry_date: string; // YYYY-MM-DD
    received_date?: string; // YYYY-MM-DD
    note?: string;
}

export interface StockReceiveResponse {
    batch_id: number;
    batch_created: boolean;
    previous_stock: string;
    new_stock: string;
    quantity_received: string;
    transaction: any;
}
