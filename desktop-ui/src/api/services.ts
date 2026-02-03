import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import {
    Article, Batch,
    WeighInDraft, CreateDraftPayload, ApprovalPayload, ApprovalResponse,
    CreateArticlePayload, CreateBatchPayload, StockReceivePayload, StockReceiveResponse,
    InventoryResponse, InventoryCountPayload, TransactionsResponse, AliasesResponse
} from './types';
import { AxiosError } from 'axios';

// --- Health ---
export const checkHealth = async () => {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH);
    return response.data;
};

// --- Articles ---
export const getArticles = async (active: 'true' | 'false' | 'all' = 'true') => {
    const response = await apiClient.get<{ items: Article[], total: number }>(API_ENDPOINTS.ARTICLES.LIST, {
        params: { active }
    });
    return response.data;
};

export const createArticle = async (data: CreateArticlePayload) => {
    const response = await apiClient.post<Article>(API_ENDPOINTS.ARTICLES.CREATE, data);
    return response.data;
};

export const archiveArticle = async (id: number) => {
    const response = await apiClient.post(API_ENDPOINTS.ARTICLES.ARCHIVE(id));
    return response.data;
};

export const restoreArticle = async (id: number) => {
    const response = await apiClient.post(API_ENDPOINTS.ARTICLES.RESTORE(id));
    return response.data;
};

export const deleteArticle = async (id: number) => {
    const response = await apiClient.delete(API_ENDPOINTS.ARTICLES.DELETE(id));
    return response.data;
};

// --- Batches ---
export const getBatchesByArticle = async (articleNo: string) => {
    const response = await apiClient.get<{ items: Batch[], total: number }>(
        API_ENDPOINTS.BATCHES.LIST_BY_ARTICLE(articleNo)
    );
    return response.data;
};

export const createBatch = async (data: CreateBatchPayload) => {
    const response = await apiClient.post<Batch>(API_ENDPOINTS.BATCHES.CREATE, data);
    return response.data;
};

// --- Drafts ---
export const getDrafts = async (status?: string) => {
    const response = await apiClient.get<{ items: WeighInDraft[], total: number }>(API_ENDPOINTS.DRAFTS.LIST, {
        params: { status }
    });
    return response.data;
};

export const createDraft = async (data: CreateDraftPayload) => {
    const response = await apiClient.post<WeighInDraft>(API_ENDPOINTS.DRAFTS.CREATE, data);
    return response.data;
};

export const approveDraft = async (id: number, data: ApprovalPayload) => {
    const response = await apiClient.post<ApprovalResponse>(API_ENDPOINTS.DRAFTS.APPROVE(id), data);
    return response.data;
};

export const rejectDraft = async (id: number, data: ApprovalPayload) => {
    const response = await apiClient.post<ApprovalResponse>(API_ENDPOINTS.DRAFTS.REJECT(id), data);
    return response.data;
};

// --- Inventory ---
export const getInventorySummary = async (filters?: { article_id?: number, batch_id?: number, location_id?: number }) => {
    const response = await apiClient.get<InventoryResponse>(API_ENDPOINTS.INVENTORY.SUMMARY, {
        params: filters
    });
    return response.data;
};

export const performInventoryCount = async (data: InventoryCountPayload) => {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.COUNT, data);
    return response.data;
};

export const receiveStock = async (data: StockReceivePayload) => {
    const response = await apiClient.post<StockReceiveResponse>(API_ENDPOINTS.INVENTORY.RECEIVE, data);
    return response.data;
};


// --- Transactions ---
export const getTransactions = async (params?: any) => {
    const response = await apiClient.get<TransactionsResponse>(API_ENDPOINTS.TRANSACTIONS.LIST, {
        params
    });
    return response.data;
};

// --- Aliases ---
export const getAliases = async (articleId: number) => {
    const response = await apiClient.get<AliasesResponse>(API_ENDPOINTS.ALIASES.LIST(articleId));
    return response.data;
};

export const createAlias = async (articleId: number, alias: string) => {
    const response = await apiClient.post(API_ENDPOINTS.ALIASES.CREATE(articleId), { alias });
    return response.data;
};

export const deleteAlias = async (articleId: number, aliasId: number) => {
    const response = await apiClient.delete(API_ENDPOINTS.ALIASES.DELETE(articleId, aliasId));
    return response.data;
};

// --- Helpers ---
export const extractErrorMessage = (error: unknown): string => {
    try {
        if (error instanceof AxiosError && error.response?.data) {
            const data = error.response.data as any;

            // 1. Handle string/html response
            if (typeof data === 'string') return data;

            // 2. Handle Flask-JWT-Extended style { msg: "..." }
            if (data.msg) return data.msg;

            // 3. Handle generic { message: "..." }
            if (data.message) return data.message;

            // 4. Handle structured ApiErrorResponse { error: { message: "..." } }
            if (data.error?.message) {
                if (data.error.details && Object.keys(data.error.details).length > 0) {
                    const detailsStr = Object.entries(data.error.details).map(([k, v]) => `${k}: ${v}`).join(', ');
                    return `${data.error.message} (${detailsStr})`;
                }
                return data.error.message;
            }
        }
    } catch (e) {
        return 'Failed to parse error message';
    }
    return (error as Error).message || 'Unknown error occurred';
};
