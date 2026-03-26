import os
from dotenv import load_dotenv

load_dotenv()


_INSECURE_DEFAULTS = {
    'dev-secret-key-change-in-production',
    'dev-jwt-secret-change-in-production',
    'dev-secret-key-document-validator-2026',
    'dev-jwt-secret-document-validator-2026',
}


class Config:
    """Base configuration."""
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    SECRET_KEY = os.getenv('SECRET_KEY', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')

    @classmethod
    def validate_secrets(cls):
        """Reject weak / missing secrets to prevent token-forgery attacks."""
        if not cls.SECRET_KEY or cls.SECRET_KEY in _INSECURE_DEFAULTS:
            raise ValueError(
                'SECRET_KEY is missing or insecure. '
                'Set a strong, random SECRET_KEY in your .env file.'
            )
        if not cls.JWT_SECRET_KEY or cls.JWT_SECRET_KEY in _INSECURE_DEFAULTS:
            raise ValueError(
                'JWT_SECRET_KEY is missing or insecure. '
                'Set a strong, random JWT_SECRET_KEY in your .env file.'
            )

    # Resolve UPLOAD_FOLDER — if env var is relative, make it absolute relative to backend dir
    _upload_env = os.getenv('UPLOAD_FOLDER')
    if _upload_env and not os.path.isabs(_upload_env):
        UPLOAD_FOLDER = os.path.join(_BASE_DIR, _upload_env)
    else:
        UPLOAD_FOLDER = _upload_env or os.path.join(_BASE_DIR, 'uploads')

    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', '16')) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    AI_PIPELINE_URL = os.getenv('AI_PIPELINE_URL', 'http://localhost:8001/api/pipeline/full/')
    AI_OCR_URL = os.getenv('AI_OCR_URL', 'http://localhost:8001/api/ocr/extract/')
    AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv('AI_REQUEST_TIMEOUT_SECONDS', '60'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(Config._BASE_DIR, 'dev.db')
    )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    def __init__(self):
        self.validate_secrets()
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError('DATABASE_URL must be set in production')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    RATELIMIT_ENABLED = False  # Disable rate limiting during tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = os.path.join(Config._BASE_DIR, 'test_uploads')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
