"""Reports API endpoints."""
from datetime import datetime, timezone
import io
from flask import send_file
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..auth import require_roles
from ..models import Transaction
from ..services import report_service
from ..schemas.reports import (
    InventurnaReportResponseSchema,
    SurplusReportResponseSchema,
    ConsumptionReportResponseSchema,
    ReorderRiskReportResponseSchema,
    TopConsumerSchema,
    ReportingStatsSchema,
    TransactionReportSchema,
    ReportQuerySchema
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'reports',
    __name__,
    url_prefix='/api/reports',
    description='Inventory and transaction reports'
)


@blp.route('/inventurna')
class InventurnaReport(MethodView):
    """Inventory count list report."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, InventurnaReportResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Get inventory count list (Article+Batch)."""
        location_id = query_args.get('location_id', 13)
        items = report_service.get_inventurna_lista(location_id)
        return {
            'items': items,
            'total': len(items),
            'generated_at': datetime.now(timezone.utc)
        }


@blp.route('/inventurna/export/excel')
class InventurnaExportExcel(MethodView):
    """Export inventory count list to Excel."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Download Inventurna list as Excel."""
        location_id = query_args.get('location_id', 13)
        excel_file = report_service.export_inventurna_to_excel(location_id)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"inventurna_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )


@blp.route('/inventurna/export/pdf')
class InventurnaExportPDF(MethodView):
    """Export inventory count list to PDF."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Download Inventurna list as PDF."""
        location_id = query_args.get('location_id', 13)
        pdf_content = report_service.export_inventurna_to_pdf(location_id)
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"inventurna_{datetime.now().strftime('%Y%m%d')}.pdf"
        )


@blp.route('/surplus')
class SurplusReport(MethodView):
    """Surplus report."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, SurplusReportResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Get surplus list."""
        location_id = query_args.get('location_id', 13)
        items = report_service.get_surplus_lista(location_id)
        return {'items': items, 'total': len(items)}


@blp.route('/surplus/export/excel')
class SurplusExportExcel(MethodView):
    """Export surplus report to Excel."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Download Surplus list as Excel."""
        location_id = query_args.get('location_id', 13)
        excel_file = report_service.export_surplus_to_excel(location_id)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"surplus_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )


@blp.route('/surplus/export/pdf')
class SurplusExportPDF(MethodView):
    """Export surplus report to PDF."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Download Surplus list as PDF."""
        location_id = query_args.get('location_id', 13)
        pdf_content = report_service.export_surplus_to_pdf(location_id)
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"surplus_{datetime.now().strftime('%Y%m%d')}.pdf"
        )


@blp.route('/statistics/consumption')
class ConsumptionReport(MethodView):
    """Consumption statistics."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, ConsumptionReportResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Get article consumption stats."""
        days = query_args.get('days', 30)
        items = report_service.get_consumption_stats(days)
        return {'items': items, 'total': len(items)}


@blp.route('/statistics/reorder-risk')
class ReorderRiskReport(MethodView):
    """Reorder risk report."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, ReorderRiskReportResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Get articles at risk of low stock."""
        location_id = query_args.get('location_id', 13)
        state_filter = query_args.get('state', 'active')
        include_green = query_args.get('include_green', False)
        
        items = report_service.get_reorder_risk_lista(
            location_id, 
            state_filter=state_filter, 
            include_green=include_green
        )
        return {'items': items, 'total': len(items)}


@blp.route('/statistics/top-consumers')
class TopConsumersStats(MethodView):
    """Top-20 monthly consumers statistics."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, TopConsumerSchema(many=True))
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """Get top 20 consumers in the last 30 days."""
        return report_service.get_top_20_monthly_consumers()


@blp.route('/statistics/reporting')
class ReportingStats(MethodView):
    """Missing Article report statistics."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, ReportingStatsSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """Get aggregate stats for missing article reports."""
        return report_service.get_reporting_stats()


@blp.route('/transactions')
class TransactionReport(MethodView):
    """Transaction report (DEPRECATED fallback)."""
    
    @blp.doc(
        security=[{'bearerAuth': []}],
        deprecated=True,
        description="Legacy transaction report. Use module-level reports and statistics instead."
    )
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, TransactionReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, query_args):
        """Legacy transaction history for audit."""
        query = Transaction.query
        
        if query_args.get('location_id'):
            query = query.filter_by(location_id=query_args['location_id'])
        if query_args.get('article_id'):
            query = query.filter_by(article_id=query_args['article_id'])
        if query_args.get('from_date'):
            query = query.filter(Transaction.occurred_at >= query_args['from_date'])
        if query_args.get('to_date'):
            query = query.filter(Transaction.occurred_at <= query_args['to_date'])
        
        transactions = query.order_by(Transaction.occurred_at.desc()).limit(1000).all()
        
        return {
            'items': [tx.to_dict() for tx in transactions],
            'total': len(transactions),
            'generated_at': datetime.now(timezone.utc)
        }
