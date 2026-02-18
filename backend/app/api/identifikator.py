"""Article Identifikator API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..auth import require_roles
from ..services import identifikator_service
from ..schemas.identifikator import (
    ArticleLookupQuerySchema,
    MissingArticleReportCreateSchema,
    MissingArticleReportSchema,
    AdminReportUpdateSchema
)
from ..schemas.articles import ArticleSchema
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'identifikator',
    __name__,
    url_prefix='/api/identifikator',
    description='Article Identifikator and missing item reporting'
)


@blp.route('/lookup')
class ArticleLookup(MethodView):
    """Article lookup (Search by No, Alias, or Description)."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ArticleLookupQuerySchema, location='query')
    @blp.response(200, ArticleSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
    def get(self, query_args):
        """Lookup article by normalized input string."""
        article = identifikator_service.identify_article(query_args['query'])
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f"No article found for '{query_args['query']}'"
                }
            }, 404
        return article


@blp.route('/report')
class MissingArticleReportCreate(MethodView):
    """Submit a report for a missing article."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(MissingArticleReportCreateSchema)
    @blp.response(201, MissingArticleReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    def post(self, report_data):
        """Submit report for article not found in system."""
        actor_user_id = int(get_jwt_identity())
        report = identifikator_service.submit_missing_article_report(
            raw_input=report_data['raw_input'],
            location_id=report_data['location_id'],
            actor_user_id=actor_user_id
        )
        db.session.commit()
        return report, 201


@blp.route('/admin/queue')
class AdminReportQueue(MethodView):
    """Admin queue for processing missing article reports (Legacy)."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, MissingArticleReportSchema(many=True))
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """List all pending missing article reports."""
        headers = {
            'Deprecation': 'true',
            'Sunset': 'Mon, 01 Jun 2026 00:00:00 GMT',
            'Link': '</api/admin/identifikator/queue>; rel="replacement"'
        }
        return identifikator_service.get_report_queue(), 200, headers


@blp.route('/admin/queue/<int:report_id>')
class AdminReportDetail(MethodView):
    """Update missing article report status (Legacy)."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(AdminReportUpdateSchema)
    @blp.response(200, MissingArticleReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Report not found')
    @jwt_required()
    @require_roles('ADMIN')
    def patch(self, update_data, report_id):
        """Update report status."""
        actor_user_id = int(get_jwt_identity())
        report = identifikator_service.update_report_status(
            report_id=report_id,
            status=update_data['status'],
            actor_user_id=actor_user_id,
            admin_note=update_data.get('admin_note'),
            resolved_article_id=update_data.get('resolved_article_id')
        )
        db.session.commit()
        headers = {
            'Deprecation': 'true',
            'Sunset': 'Mon, 01 Jun 2026 00:00:00 GMT',
            'Link': f'</api/admin/identifikator/queue/{report_id}>; rel="replacement"'
        }
        return report, 200, headers


# --- NEW CONTRACT: /api/admin/identifikator ---

blp_admin = Blueprint(
    'admin_identifikator',
    __name__,
    url_prefix='/api/admin/identifikator',
    description='New Contract for Identifikator Admin'
)

@blp_admin.route('/queue')
class NewAdminReportQueue(MethodView):
    @blp_admin.doc(security=[{'bearerAuth': []}])
    @blp_admin.response(200, MissingArticleReportSchema(many=True))
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """Correct contract for report queue."""
        return identifikator_service.get_report_queue()

@blp_admin.route('/queue/<int:report_id>')
class NewAdminReportDetail(MethodView):
    @blp_admin.doc(security=[{'bearerAuth': []}])
    @blp_admin.arguments(AdminReportUpdateSchema)
    @blp_admin.response(200, MissingArticleReportSchema)
    @jwt_required()
    @require_roles('ADMIN')
    def patch(self, update_data, report_id):
        """Correct contract for report resolution."""
        actor_user_id = int(get_jwt_identity())
        report = identifikator_service.update_report_status(
            report_id=report_id,
            status=update_data['status'],
            actor_user_id=actor_user_id,
            admin_note=update_data.get('admin_note'),
            resolved_article_id=update_data.get('resolved_article_id')
        )
        db.session.commit()
        return report
