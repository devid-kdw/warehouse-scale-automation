"""API package - registers all blueprints."""
from .health import blp as health_blp
from .articles import blp as articles_blp
from .batches import blp as batches_blp
from .drafts import blp as drafts_blp
from .approvals import blp as approvals_blp
from .reports import blp as reports_blp


def register_blueprints(api):
    """Register all API blueprints with flask-smorest Api."""
    api.register_blueprint(health_blp)
    api.register_blueprint(articles_blp)
    api.register_blueprint(batches_blp)
    api.register_blueprint(drafts_blp)
    api.register_blueprint(approvals_blp)
    api.register_blueprint(reports_blp)
