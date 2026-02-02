"""Application configuration loaded from environment variables."""
import os
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
    
    # Security
    API_TOKEN = os.getenv('API_TOKEN', '')
    ALLOW_NO_AUTH_IN_DEV = os.getenv('ALLOW_NO_AUTH_IN_DEV', 'false').lower() == 'true'
    
    # CORS configuration
    # Comma-separated list of allowed origins
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://localhost:3000'
    )
    # Allow all origins (dev only - use with caution)
    CORS_ALLOW_ALL = os.getenv('CORS_ALLOW_ALL', 'false').lower() == 'true'
    
    # API documentation
    API_TITLE = 'Warehouse Scale Automation API'
    API_VERSION = '0.1.0'
    OPENAPI_VERSION = '3.0.3'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    OPENAPI_JSON_PATH = '/openapi.json'
    
    # OpenAPI security scheme
    API_SPEC_OPTIONS = {
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'API Token'
                }
            }
        }
    }
    
    # Business rules
    QUANTITY_MIN = 0.01
    QUANTITY_MAX = 9999.99
    
    @classmethod
    def get_cors_origins(cls):
        """Parse CORS_ORIGINS into a list."""
        if cls.CORS_ALLOW_ALL:
            return '*'
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(',') if origin.strip()]
