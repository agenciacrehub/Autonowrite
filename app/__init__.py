from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from .template_filters import timesince

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Import models here to avoid circular imports
from app.models.user import User
from app.models.project import Project
from app.models.execution import Execution, ExecutionLog, ExecutionStatus, ExecutionLogLevel

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class is None:
        from config import Config
        config_class = Config
    app.config.from_object(config_class)
    
    # Force SQLite database for development
    import os
    if 'DATABASE_URL' not in os.environ or 'postgresql' in os.environ.get('DATABASE_URL', ''):
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.wizard import bp as wizard_bp
    from app.routes.execution import bp as execution_bp
    from app.routes.results import bp as results_bp
    from app.routes.projects import bp as projects_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(wizard_bp, url_prefix='/wizard')
    app.register_blueprint(execution_bp, url_prefix='/execution')
    app.register_blueprint(results_bp, url_prefix='/project')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    
    # Register template filters
    app.jinja_env.filters['timesince'] = timesince
    
    # Initialize database tables
    with app.app_context():
        # This will create the database file using SQLite
        db.create_all()
        
        # Create admin user if not exists
        from werkzeug.security import generate_password_hash
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app

from app import models  # noqa
