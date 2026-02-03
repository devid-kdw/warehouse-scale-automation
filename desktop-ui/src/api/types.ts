// API Data Types matching Backend DTOs

export interface Article {
    id: number;
    article_no: string;
    description: string | null;
    article_group: string | null; // e.g., "Paints", "Consumables" 
    base_uom: string;
    pack_size: number | null;
    pack_uom: string | null;
    barcode: string | null;
    is_paint: boolean;
    is_active: boolean;
    created_at: string;
    updated_at: string | null;
}

export interface CreateArticleRequest {
    article_no: string;
    description?: string;
    article_group?: string;
    base_uom?: string;
    pack_size?: number;
    pack_uom?: string;
    barcode?: string;
    is_paint?: boolean;
    is_active?: boolean;
}

export interface Batch {
    id: number;
    article_id: number;
    batch_code: string;
    is_active: boolean;
    created_at: string;
    updated_at: string | null;
}

export interface CreateBatchRequest {
    article_id: number;
    batch_code: string;
}

export type DraftStatus = 'DRAFT' | 'APPROVED' | 'REJECTED';

export interface WeighInDraft {
    id: number;
    location_id: number;
    article_id: number;
    batch_id: number;
    quantity_kg: number;
    client_event_id: string;
    status: DraftStatus;
    created_at: string;
    updated_at: string | null;

    // Relations (might be included if backend serializer supports nested, otherwise IDs)
    // Backend DraftSchema likely doesn't nest full objects, but we'll see.
    // We might need to join client-side if needed.
}

export interface CreateDraftRequest {
    location_id: number;
    article_id: number;
    batch_id: number;
    quantity_kg: number; // Decimal
    client_event_id: string; // UUID
    note?: string;
}

export interface ApprovalRequest {
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

export interface ErrorDetails {
    code: string;
    message: string;
    details?: Record<string, any>;
}

export interface ApiErrorResponse {
    error: ErrorDetails;
}
