"""Schemas package."""
from .common import ErrorResponseSchema, SuccessMessageSchema, PaginationSchema
from .articles import ArticleSchema, ArticleCreateSchema, ArticleListSchema
from .batches import BatchSchema, BatchCreateSchema, BatchListSchema
from .drafts import DraftSchema, DraftCreateSchema, DraftUpdateSchema, DraftQuerySchema, DraftListSchema
from .approvals import ApprovalActionSchema, ApprovalRequestSchema, ApprovalResponseSchema
from .reports import InventoryReportSchema, TransactionReportSchema, ReportQuerySchema

__all__ = [
    'ErrorResponseSchema',
    'SuccessMessageSchema',
    'PaginationSchema',
    'ArticleSchema',
    'ArticleCreateSchema',
    'ArticleListSchema',
    'BatchSchema',
    'BatchCreateSchema',
    'BatchListSchema',
    'DraftSchema',
    'DraftCreateSchema',
    'DraftUpdateSchema',
    'DraftQuerySchema',
    'DraftListSchema',
    'ApprovalActionSchema',
    'ApprovalRequestSchema',
    'ApprovalResponseSchema',
    'InventoryReportSchema',
    'TransactionReportSchema',
    'ReportQuerySchema',
]
