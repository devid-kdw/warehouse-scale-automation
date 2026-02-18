import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import {
    Article, Batch,
    WeighInDraft, CreateDraftPayload, ApprovalPayload, ApprovalResponse,
    CreateArticlePayload, CreateBatchPayload, StockReceivePayload, StockReceiveResponse,
    InventoryResponse, InventoryCountPayload, TransactionsResponse, AliasesResponse,
    DraftGroup, DraftGroupSummary, CreateDraftGroupPayload,
    ReceiptHistoryResponse, TransactionQueryParams,
    MissingItemReport, AdminReportUpdatePayload
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

export const updateArticle = async (id: number, data: Partial<CreateArticlePayload>) => {
    const response = await apiClient.patch<Article>(API_ENDPOINTS.ARTICLES.UPDATE(id), data);
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

export const resolveArticle = async (query: string) => {
    const response = await apiClient.get<Article>(API_ENDPOINTS.ARTICLES.RESOLVE, {
        params: { query }
    });
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

// --- Draft Groups ---
export const getDraftGroups = async (status?: string) => {
    const response = await apiClient.get<{ items: DraftGroupSummary[], total: number }>(API_ENDPOINTS.DRAFT_GROUPS.LIST, {
        params: { status }
    });
    return response.data;
};

export const getDraftGroup = async (id: number) => {
    const response = await apiClient.get<DraftGroup>(API_ENDPOINTS.DRAFT_GROUPS.GET(id));
    return response.data;
};

export const createDraftGroup = async (data: CreateDraftGroupPayload) => {
    const response = await apiClient.post<DraftGroup>(API_ENDPOINTS.DRAFT_GROUPS.CREATE, data);
    return response.data;
};

export const renameDraftGroup = async (id: number, name: string) => {
    const response = await apiClient.patch<DraftGroup>(API_ENDPOINTS.DRAFT_GROUPS.RENAME(id), { name });
    return response.data;
};

export const approveDraftGroup = async (id: number) => {
    const response = await apiClient.post<{ message: string }>(API_ENDPOINTS.DRAFT_GROUPS.APPROVE(id));
    return response.data;
};

export const rejectDraftGroup = async (id: number) => {
    const response = await apiClient.post<{ message: string }>(API_ENDPOINTS.DRAFT_GROUPS.REJECT(id));
    return response.data;
};

export const getDailyDrafts = async (status?: string) => {
    const response = await apiClient.get<any[]>(API_ENDPOINTS.DAILY_DRAFTS.LIST, {
        params: { status }
    });
    return response.data;
};

export const getDailyDraftDetail = async (date: string, locationId: number) => {
    const response = await apiClient.get<any>(API_ENDPOINTS.DAILY_DRAFTS.GET(date, locationId));
    return response.data;
};

export const approveDailyDrafts = async (date: string, locationId: number) => {
    const response = await apiClient.post(API_ENDPOINTS.DAILY_DRAFTS.APPROVE(date, locationId));
    return response.data;
};

export const rejectDailyDrafts = async (date: string, locationId: number) => {
    const response = await apiClient.post(API_ENDPOINTS.DAILY_DRAFTS.REJECT(date, locationId));
    return response.data;
};

export const updateDailyDraftLines = async (
    date: string,
    locationId: number,
    // P0 fix: payload is a single line edit, not an array
    lineEdit: { article_id: number; batch_id: number; new_total_qty: number }
) => {
    const response = await apiClient.patch(API_ENDPOINTS.DAILY_DRAFTS.UPDATE_LINES(date, locationId), lineEdit);
    return response.data;
};


// --- Inventory ---
export const getInventory = async (filters?: { category?: string, search?: string, state?: 'active' | 'inactive' | 'all' }) => {
    const response = await apiClient.get<InventoryResponse>(API_ENDPOINTS.INVENTORY.LIST, {
        params: filters
    });
    return response.data;
};

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

export const getReceiptHistory = async () => {
    const response = await apiClient.get<ReceiptHistoryResponse>(API_ENDPOINTS.INVENTORY.RECEIPTS);
    return response.data;
};


// --- Transactions ---
export const getTransactions = async (params?: TransactionQueryParams) => {
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

// --- Reports ---
export const getInventurnaLista = async () => {
    const response = await apiClient.get<any>(API_ENDPOINTS.REPORTS.INVENTURNA);
    return response.data;
};

export const getSurplusLista = async () => {
    const response = await apiClient.get<any>(API_ENDPOINTS.REPORTS.SURPLUS);
    return response.data;
};

export const getStatistics = async (type: 'consumption' | 'reorder-risk' | 'top-consumers') => {
    let url: string = API_ENDPOINTS.REPORTS.STATISTICS.CONSUMPTION;
    if (type === 'reorder-risk') url = API_ENDPOINTS.REPORTS.STATISTICS.REORDER_RISK;
    if (type === 'top-consumers') url = API_ENDPOINTS.REPORTS.STATISTICS.TOP_CONSUMERS;

    const response = await apiClient.get<any>(url);
    return response.data;
};

// Auth-safe blob export (P1 fix: use apiClient with Bearer token, not window.open)
export const downloadReportExport = async (
    type: 'inventurna' | 'surplus',
    format: 'excel' | 'pdf'
): Promise<void> => {
    const url = API_ENDPOINTS.REPORTS.EXPORT(type, format);
    const response = await apiClient.get(url, { responseType: 'blob' });
    const blob = new Blob([response.data], {
        type: format === 'excel'
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            : 'application/pdf'
    });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = `${type}_${new Date().toISOString().slice(0, 10)}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(objectUrl);
};

/** @deprecated Use downloadReportExport instead */
export const getReportExportUrl = (type: 'inventurna' | 'surplus', format: 'excel' | 'pdf') => {
    return API_ENDPOINTS.REPORTS.EXPORT(type, format);
};

// --- Identifikator (P0 fix: correct endpoints, params, and payloads) ---

/** Lookup article by code, name, or alias. Backend returns single article or 404. */
export const lookupArticle = async (query: string): Promise<Article | null> => {
    try {
        const response = await apiClient.get<Article>(API_ENDPOINTS.IDENTIFIKATOR.LOOKUP, {
            params: { query }  // P0 fix: param is 'query' not 'q'
        });
        return response.data;
    } catch (e: any) {
        if (e?.response?.status === 404) return null;
        throw e;
    }
};

/** @deprecated Use lookupArticle instead */
export const searchArticles = lookupArticle as any;

/** Submit a missing article report. P0 fix: payload is {raw_input, location_id} */
export const reportMissingItem = async (rawInput: string, locationId: number = 13) => {
    const response = await apiClient.post(API_ENDPOINTS.IDENTIFIKATOR.REPORT_MISSING, {
        raw_input: rawInput,
        location_id: locationId
    });
    return response.data;
};

/** Get admin queue of pending missing article reports. */
export const getIdentifierQueue = async (): Promise<MissingItemReport[]> => {
    const response = await apiClient.get<MissingItemReport[]>(API_ENDPOINTS.IDENTIFIKATOR.ADMIN_QUEUE);
    // Backend returns array directly (not wrapped in {items: [...]})
    return Array.isArray(response.data) ? response.data : (response.data as any).items || [];
};

/** Resolve a missing article report. P0 fix: uses PATCH not POST. */
export const resolveMissingReport = async (id: number, payload: AdminReportUpdatePayload) => {
    const response = await apiClient.patch(API_ENDPOINTS.IDENTIFIKATOR.RESOLVE(id), payload);
    return response.data;
};
