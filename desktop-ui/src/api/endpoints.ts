// Centralized API Endpoints
// Strictly adhering to backend structure

export const API_ENDPOINTS = {
    HEALTH: '/health',

    ARTICLES: {
        LIST: '/api/articles',
        CREATE: '/api/articles',
        RESOLVE: '/api/articles/resolve',
        GET: (articleNo: string) => `/api/articles/${articleNo}`,
        UPDATE: (id: number) => `/api/articles/id/${id}`,  // P0 fix: must be /api/articles/id/<id>
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
        LIST: '/api/inventory',
        INSPECT: (articleId: number) => `/api/inventory/${articleId}/inspect`,
        SUMMARY: '/api/inventory/summary',
        COUNT: '/api/inventory/count',
        ADJUST: '/api/inventory/adjust',
        RECEIVE: '/api/inventory/receive',
        RECEIPTS: '/api/inventory/receipts',
    },

    TRANSACTIONS: {
        LIST: '/api/transactions',
    },

    REPORTS: {
        INVENTURNA: '/api/reports/inventurna',
        SURPLUS: '/api/reports/surplus',
        STATISTICS: {
            CONSUMPTION: '/api/reports/statistics/consumption',
            REORDER_RISK: '/api/reports/statistics/reorder-risk',
            TOP_CONSUMERS: '/api/reports/statistics/top-consumers',
        },
        EXPORT: (type: 'inventurna' | 'surplus', format: 'excel' | 'pdf') => `/api/reports/${type}/export/${format}`,
    },

    // P0 fix: Identifikator canonical contract
    IDENTIFIKATOR: {
        LOOKUP: '/api/identifikator/lookup',       // GET ?query=...
        REPORT_MISSING: '/api/identifikator/report', // POST {raw_input, location_id}
        ADMIN_QUEUE: '/api/admin/identifikator/queue',  // GET
        RESOLVE: (id: number) => `/api/admin/identifikator/queue/${id}`, // PATCH
    },

    ALIASES: {
        LIST: (articleId: number) => `/api/articles/${articleId}/aliases`,
        CREATE: (articleId: number) => `/api/articles/${articleId}/aliases`,
        DELETE: (articleId: number, aliasId: number) => `/api/articles/${articleId}/aliases/${aliasId}`,
    },

    DRAFT_GROUPS: {
        LIST: '/api/draft-groups',
        CREATE: '/api/draft-groups',
        GET: (id: number) => `/api/draft-groups/${id}`,
        RENAME: (id: number) => `/api/draft-groups/${id}`,
        APPROVE: (id: number) => `/api/draft-groups/${id}/approve`,
        REJECT: (id: number) => `/api/draft-groups/${id}/reject`,
    },

    DAILY_DRAFTS: {
        LIST: '/api/drafts/daily',
        GET: (date: string, locationId: number) => `/api/drafts/daily/${date}/${locationId}`,
        APPROVE: (date: string, locationId: number) => `/api/drafts/daily/${date}/${locationId}/approve`,
        REJECT: (date: string, locationId: number) => `/api/drafts/daily/${date}/${locationId}/reject`,
        UPDATE_LINES: (date: string, locationId: number) => `/api/drafts/daily/${date}/${locationId}/lines`,
    }
} as const;
