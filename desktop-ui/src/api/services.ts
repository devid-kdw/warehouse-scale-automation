import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import {
    Article, Batch,
    WeighInDraft, CreateDraftRequest, ApprovalRequest, ApprovalResponse,
    CreateArticleRequest, CreateBatchRequest,
    ApiErrorResponse
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

export const createArticle = async (data: CreateArticleRequest) => {
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

export const createBatch = async (data: CreateBatchRequest) => {
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

export const createDraft = async (data: CreateDraftRequest) => {
    const response = await apiClient.post<WeighInDraft>(API_ENDPOINTS.DRAFTS.CREATE, data);
    return response.data;
};

export const approveDraft = async (id: number, data: ApprovalRequest) => {
    const response = await apiClient.post<ApprovalResponse>(API_ENDPOINTS.DRAFTS.APPROVE(id), data);
    return response.data;
};

export const rejectDraft = async (id: number, data: ApprovalRequest) => {
    const response = await apiClient.post<ApprovalResponse>(API_ENDPOINTS.DRAFTS.REJECT(id), data);
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
