"""Common Marshmallow schemas for API responses."""
from marshmallow import Schema, fields


class ErrorDetailSchema(Schema):
    """Error detail schema."""
    code = fields.String(required=True, metadata={'description': 'Error code'})
    message = fields.String(required=True, metadata={'description': 'Human-readable message'})
    details = fields.Dict(keys=fields.String(), metadata={'description': 'Additional details'})


class ErrorResponseSchema(Schema):
    """Standard error response wrapper."""
    error = fields.Nested(ErrorDetailSchema, required=True)


class SuccessMessageSchema(Schema):
    """Simple success message."""
    message = fields.String(required=True)


class PaginationSchema(Schema):
    """Pagination query parameters."""
    page = fields.Integer(load_default=1, metadata={'description': 'Page number'})
    per_page = fields.Integer(load_default=50, metadata={'description': 'Items per page'})


class NotImplementedSchema(Schema):
    """Not implemented response."""
    error = fields.Nested(ErrorDetailSchema, required=True)
