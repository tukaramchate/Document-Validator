import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

    # Resolve UPLOAD_FOLDER — if env var is relative, make it absolute relative to backend dir
    _upload_env = os.getenv('UPLOAD_FOLDER')
    if _upload_env and not os.path.isabs(_upload_env):
        UPLOAD_FOLDER = os.path.join(_BASE_DIR, _upload_env)
    else:
        UPLOAD_FOLDER = _upload_env or os.path.join(_BASE_DIR, 'uploads')

    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', '16')) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
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


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = os.path.join(Config._BASE_DIR, 'test_uploads')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
