// Centralized API Endpoints
// Strictly adhering to backend structure

export const API_ENDPOINTS = {
    HEALTH: '/health',

    ARTICLES: {
        LIST: '/api/articles',
        CREATE: '/api/articles',
        GET: (articleNo: string) => `/api/articles/${articleNo}`,
        ARCHIVE: (id: number) => `/api/articles/${id}/archive`,
        RESTORE: (id: number) => `/api/articles/${id}/restore`,
        DELETE: (id: number) => `/api/articles/${id}`,
    },

    BATCHES: {
        CREATE: '/api/batches',
        // Confirmed: backend uses /api/articles/<article_no>/batches
        LIST_BY_ARTICLE: (articleNo: string) => `/api/articles/${articleNo}/batches`,
    },

    DRAFTS: {
        LIST: '/api/drafts',
        CREATE: '/api/drafts',
        GET: (id: number) => `/api/drafts/${id}`,
        APPROVE: (id: number) => `/api/drafts/${id}/approve`,
        REJECT: (id: number) => `/api/drafts/${id}/reject`,
    },

    INVENTORY: {
        SUMMARY: '/api/inventory/summary',
        COUNT: '/api/inventory/count',
        ADJUST: '/api/inventory/adjust',
        RECEIVE: '/api/inventory/receive',
    },

    TRANSACTIONS: {
        LIST: '/api/transactions',
    },

    ALIASES: {
        LIST: (articleId: number) => `/api/articles/${articleId}/aliases`,
        CREATE: (articleId: number) => `/api/articles/${articleId}/aliases`,
        DELETE: (articleId: number, aliasId: number) => `/api/articles/${articleId}/aliases/${aliasId}`,
    }
} as const;
