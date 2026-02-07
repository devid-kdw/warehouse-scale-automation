"""Draft Groups API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..auth import require_roles
from ..models import DraftGroup, Location
from ..services import draft_group_service
from ..error_handling import AppError, InsufficientStockError
from ..schemas.draft_groups import (
    DraftGroupSchema, DraftGroupCreateSchema, 
    DraftGroupListSchema, DraftGroupSummarySchema,
    DraftGroupUpdateSchema
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'draft_groups',
    __name__,
    url_prefix='/api/draft-groups',
    description='Draft groups management'
)


@blp.route('')
class DraftGroupList(MethodView):
    """Draft group collection resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftGroupListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    def get(self):
        """List draft groups.
        
        Returns groups with summary info (total qty, line count).
        """
        groups = DraftGroup.query.order_by(DraftGroup.created_at.desc()).all()
        return {
            'items': groups,
            'total': len(groups)
        }
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DraftGroupCreateSchema)
    @blp.response(201, DraftGroupSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Location not found')
    @jwt_required()
    def post(self, group_data):
        """Create a new draft group with multiple lines.
        
        Accessible by ADMIN and OPERATOR.
        """
        current_user_id = int(get_jwt_identity())
        
        try:
            group = draft_group_service.create_group(
                location_id=group_data['location_id'],
                user_id=current_user_id,
                lines=group_data['lines'],
                name=group_data.get('name')
            )
            return group, 201
        except AppError as e:
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, 400


@blp.route('/<int:group_id>')
class DraftGroupDetail(MethodView):
    """Single draft group resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftGroupSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Group not found')
    @jwt_required()
    def get(self, group_id):
        """Get draft group by ID with lines."""
        group = db.session.get(DraftGroup, group_id)
        if not group:
            return {
                'error': {
                    'code': 'GROUP_NOT_FOUND',
                    'message': f'Group {group_id} not found',
                    'details': {}
                }
            }, 404
        return group
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DraftGroupUpdateSchema)
    @blp.response(200, DraftGroupSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Draft not in DRAFT status')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Group not found')
    @jwt_required()
    def patch(self, group_data, group_id):
        """Update draft group (e.g. rename)."""
        current_user_id = int(get_jwt_identity())
        
        try:
            group = draft_group_service.update_group_name(
                group_id=group_id,
                name=group_data['name'],
                actor_user_id=current_user_id
            )
            return group
        except AppError as e:
            status_code = 404 if 'NOT_FOUND' in e.code else 400
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, status_code


@blp.route('/<int:group_id>/approve')
class ApproveGroup(MethodView):
    """Approve a draft group resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftGroupSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin required')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Conflict / Insufficient stock')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, group_id):
        """Atomic group approval."""
        current_user_id = int(get_jwt_identity())
        
        try:
            result = draft_group_service.approve_group(group_id, current_user_id)
            group = db.session.get(DraftGroup, group_id)
            return group
        except InsufficientStockError as e:
            db.session.rollback()
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, 409
        except AppError as e:
            db.session.rollback()
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, 409


@blp.route('/<int:group_id>/reject')
class RejectGroup(MethodView):
    """Reject a draft group resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftGroupSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin required')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, group_id):
        """Atomic group rejection."""
        current_user_id = int(get_jwt_identity())
        
        try:
            draft_group_service.reject_group(group_id, current_user_id)
            group = db.session.get(DraftGroup, group_id)
            return group
        except AppError as e:
            db.session.rollback()
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, 409
