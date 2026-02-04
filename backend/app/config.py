"""Application configuration loaded from environment variables."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://localhost:5432/warehouse'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # Server
    APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
    APP_PORT = int(os.getenv('APP_PORT', 5001))
    ENV = os.getenv('ENV', 'development')
    DEBUG = ENV == 'development'
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_ACCESS_EXPIRES_MINUTES', 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_EXPIRES_DAYS', 7)))  # 7 days per spec
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Legacy API Token (deprecated, for backward compatibility only)
    API_TOKEN = os.getenv('API_TOKEN', '')
    ALLOW_NO_AUTH_IN_DEV = os.getenv('ALLOW_NO_AUTH_IN_DEV', 'false').lower() == 'true'
    
    # CORS configuration
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://localhost:3000'
    )
    CORS_ALLOW_ALL = os.getenv('CORS_ALLOW_ALL', 'false').lower() == 'true'
    
    # API documentation
    API_TITLE = 'Warehouse Scale Automation API'
    API_VERSION = '0.1.0'
    OPENAPI_VERSION = '3.0.3'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    OPENAPI_JSON_PATH = '/openapi.json'
    
    # OpenAPI security scheme - JWT Bearer
    API_SPEC_OPTIONS = {
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }
    }
    
    # Business rules
    QUANTITY_MIN = 0.01
    QUANTITY_MAX = 9999.99
    
    # JWT Security settings
    JWT_MIN_SECRET_LENGTH = 32
    
    @classmethod
    def get_cors_origins(cls):
        """Parse CORS_ORIGINS into a list."""
        if cls.CORS_ALLOW_ALL:
            return '*'
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(',') if origin.strip()]
    
    @classmethod
    def validate_production_config(cls):
        """Validate required config for production environment."""
        if cls.ENV == 'production':
            # Check for default/weak JWT secret
            if cls.JWT_SECRET_KEY == 'dev-secret-change-in-production':
                raise RuntimeError(
                    "SECURITY ERROR: JWT_SECRET_KEY must be set in production. "
                    "Set a strong random secret via environment variable."
                )
            # Check minimum secret length
            if len(cls.JWT_SECRET_KEY) < cls.JWT_MIN_SECRET_LENGTH:
                raise RuntimeError(
                    f"SECURITY ERROR: JWT_SECRET_KEY must be at least {cls.JWT_MIN_SECRET_LENGTH} characters. "
                    f"Current length: {len(cls.JWT_SECRET_KEY)}"
                )

