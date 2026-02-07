"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# API (flask-smorest)
api = Api()

# JWT Authentication
jwt = JWTManager()

# Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
