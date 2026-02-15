import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 20
    }

class DevelopmentConfig(Config):
    # Use SQLite for development by default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class ProductionConfig(Config):
    # Prepare for MariaDB/PostgreSQL
    # Example format: mysql+pymysql://user:password@host/db_name
    # or: postgresql://user:password@host/db_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Usar chaves do ambiente se disponíveis
    _secret = os.environ.get('SECRET_KEY')
    _jwt_secret = os.environ.get('JWT_SECRET_KEY')
    
    if _secret:
        SECRET_KEY = _secret
    if _jwt_secret:
        JWT_SECRET_KEY = _jwt_secret

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
