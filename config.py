import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Use SQLite for development by default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class ProductionConfig(Config):
    # Prepare for MariaDB
    # Example format: mysql+pymysql://user:password@host/db_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Validar chaves secretas em produção
    def __init__(self):
        super().__init__()
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY deve ser definida em produção!")
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError("JWT_SECRET_KEY deve ser definida em produção!")
        
        # Sobrescrever com valores do ambiente
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
