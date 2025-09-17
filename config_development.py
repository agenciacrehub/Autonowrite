import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class DevelopmentConfig:
    # App
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    
    # Database - Force SQLite for development (override any DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or ('sqlite:///' + os.path.join(basedir, 'app.db'))
    if 'postgresql' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_TYPE = 'filesystem'
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Disable CSRF for API testing
    WTF_CSRF_ENABLED = False

# Use this config for development
config = DevelopmentConfig
