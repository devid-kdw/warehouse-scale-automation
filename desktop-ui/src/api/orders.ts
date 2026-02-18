import { apiClient } from './client';

export interface OrderLine {
    id: number;
    order_id: number;
    article_id: number;
    article_no: string;
    ordered_qty: string;
    received_qty: string;
    uom: string;
    delivery_date: string | null;
    status: 'OPEN' | 'CLOSED' | 'REMOVED';
    note: string | null;
}

export interface Order {
    id: number;
    order_number: string;
    supplier_code: string | null;
    supplier_name: string | null;
    note: string | null;
    status: 'OPEN' | 'CLOSED';
    created_by: number;
    created_at: string;
    updated_at: string | null;
    lines: OrderLine[];
}

export interface OrderCreatePayload {
    order_number?: string; // "auto" or specific number
    supplier_code?: string;
    supplier_name?: string;
    note?: string;
    lines: {
        article_id: number;
        ordered_qty: number;
        uom: string;
        delivery_date?: string;
        note?: string;
    }[];
}

export interface OrderUpdatePayload {
    supplier_code?: string;
    supplier_name?: string;
    note?: string;
    lines?: {
        id?: number; // if updating existing line
        article_id: number;
        ordered_qty: number;
        uom: string;
        delivery_date?: string;
        note?: string;
    }[];
}

export interface OrderListResponse {
    items: Order[];
    total: number;
}

/**
 * List orders with optional status filter
 */
export async function listOrders(status: 'OPEN' | 'CLOSED' | 'all' = 'all'): Promise<OrderListResponse> {
    const response = await apiClient.get<OrderListResponse>('/api/orders', {
        params: { status },
    });
    return response.data;
}

/**
 * Get order detail with lines
 */
export async function getOrder(orderId: number): Promise<Order> {
    const response = await apiClient.get<Order>(`/api/orders/${orderId}`);
    return response.data;
}

/**
 * Create a new order
 * If order_number is omitted or "auto", backend generates ORD-xxxx
 */
export async function createOrder(data: OrderCreatePayload): Promise<Order> {
    const response = await apiClient.post<Order>('/api/orders', data);
    return response.data;
}

/**
 * Update order header and optionally replace lines
 */
export async function updateOrder(orderId: number, data: OrderUpdatePayload): Promise<Order> {
    const response = await apiClient.put<Order>(`/api/orders/${orderId}`, data);
    return response.data;
}

/**
 * Soft-remove an order line (sets status to REMOVED)
 */
export async function removeOrderLine(orderId: number, lineId: number): Promise<OrderLine> {
    const response = await apiClient.delete<OrderLine>(`/api/orders/${orderId}/lines/${lineId}`);
    return response.data;
}
