import os
import time
import logging
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from config import config_by_name
from middleware.error_handler import register_error_handlers

# Configure logging
log_handlers = [logging.StreamHandler()]
try:
    log_handlers.append(logging.FileHandler('app.log'))
except (PermissionError, OSError):
    pass  # Skip file logging if not writable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Application factory — creates and configures the Flask application."""
    app = Flask(__name__)

    # Load configuration
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.upload import upload_bp
    from blueprints.validation import validation_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(validation_bp, url_prefix='/api')

    # Register global error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'message': 'Document Validator API is running'
            }
        })

    # Request logging middleware
    @app.before_request
    def before_request_logging():
        g.request_start_time = time.time()

    @app.after_request
    def after_request_logging(response):
        duration = time.time() - getattr(g, 'request_start_time', time.time())
        logger.info(
            f'{request.method} {request.path} → {response.status_code} ({duration:.3f}s)'
        )
        return response

    # Create database tables and upload directory
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info('Database tables created and upload folder ensured')

    return app


# Run the application
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, port=5000)
