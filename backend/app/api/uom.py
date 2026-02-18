"""UOM catalog API — list and auto-create UOM entries."""
import marshmallow as ma
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..services import uom_service

blp = Blueprint('uom', __name__, url_prefix='/api/uom',
                description='Unit of Measure catalog')


class UomSchema(ma.Schema):
    """UOM catalog response schema."""
    id = ma.fields.Integer(dump_only=True)
    code = ma.fields.String(required=True)
    description = ma.fields.String(allow_none=True)
    created_at = ma.fields.DateTime(dump_only=True)


class UomListSchema(ma.Schema):
    """Paginated UOM list (flat for now)."""
    items = ma.fields.List(ma.fields.Nested(UomSchema))


@blp.route('/')
class UomList(MethodView):
    """List all UOM catalog entries."""

    @blp.response(200, UomListSchema)
    @jwt_required()
    def get(self):
        """List all units of measure in catalog.

        Any authenticated user can view.
        """
        items = uom_service.list_uom()
        return {'items': items}
