"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api

# Database
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# API (flask-smorest)
api = Api()
