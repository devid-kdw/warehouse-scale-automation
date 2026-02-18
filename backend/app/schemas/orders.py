"""Order schemas for request/response serialization."""
import marshmallow as ma
from marshmallow import validate, pre_load


class OrderLineCreateSchema(ma.Schema):
    """Schema for creating an order line."""
    article_id = ma.fields.Integer(required=True)
    ordered_qty = ma.fields.Decimal(required=True, as_string=True, places=3,
                                     validate=validate.Range(min=0.001))
    uom = ma.fields.String(required=True, validate=validate.Length(min=1, max=20))
    delivery_date = ma.fields.Date(load_default=None, allow_none=True)
    note = ma.fields.String(load_default=None, allow_none=True,
                            validate=validate.Length(max=500))


class OrderCreateSchema(ma.Schema):
    """Schema for creating an order."""
    order_number = ma.fields.String(
        load_default=None, allow_none=True,
        validate=validate.Length(min=1, max=50),
        metadata={'description': 'Order number. Omit or set to "auto" for auto-generated ORD-xxxx.'}
    )
    supplier_code = ma.fields.String(load_default=None, allow_none=True,
                                      validate=validate.Length(max=50))
    supplier_name = ma.fields.String(load_default=None, allow_none=True,
                                      validate=validate.Length(max=200))
    note = ma.fields.String(load_default=None, allow_none=True,
                            validate=validate.Length(max=500))
    lines = ma.fields.List(ma.fields.Nested(OrderLineCreateSchema), required=True,
                           validate=validate.Length(min=1))

    @pre_load
    def normalize_auto_number(self, data, **kwargs):
        """Treat 'auto' as None to trigger auto-generation."""
        if data.get('order_number') == 'auto':
            data['order_number'] = None
        return data


class OrderUpdateSchema(ma.Schema):
    """Schema for updating an order header + lines."""
    supplier_code = ma.fields.String(load_default=None, allow_none=True,
                                      validate=validate.Length(max=50))
    supplier_name = ma.fields.String(load_default=None, allow_none=True,
                                      validate=validate.Length(max=200))
    note = ma.fields.String(load_default=None, allow_none=True,
                            validate=validate.Length(max=500))
    lines = ma.fields.List(ma.fields.Nested(OrderLineCreateSchema), load_default=None,
                           allow_none=True)


class OrderLineSchema(ma.Schema):
    """Schema for order line response."""
    id = ma.fields.Integer(dump_only=True)
    order_id = ma.fields.Integer(dump_only=True)
    article_id = ma.fields.Integer()
    article_no = ma.fields.String(dump_only=True)
    ordered_qty = ma.fields.Decimal(as_string=True, places=3)
    received_qty = ma.fields.Decimal(as_string=True, places=3)
    uom = ma.fields.String()
    delivery_date = ma.fields.Date(allow_none=True)
    status = ma.fields.String()
    note = ma.fields.String(allow_none=True)


class OrderSchema(ma.Schema):
    """Schema for order response."""
    id = ma.fields.Integer(dump_only=True)
    order_number = ma.fields.String()
    supplier_code = ma.fields.String(allow_none=True)
    supplier_name = ma.fields.String(allow_none=True)
    note = ma.fields.String(allow_none=True)
    status = ma.fields.String()
    created_by = ma.fields.Integer()
    created_at = ma.fields.DateTime(dump_only=True)
    updated_at = ma.fields.DateTime(dump_only=True, allow_none=True)
    lines = ma.fields.List(ma.fields.Nested(OrderLineSchema))


class OrderListSchema(ma.Schema):
    """Schema for paginated order list."""
    items = ma.fields.List(ma.fields.Nested(OrderSchema))
    total = ma.fields.Integer()
