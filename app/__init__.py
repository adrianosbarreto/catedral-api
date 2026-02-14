from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configurar APPLICATION_ROOT se definido no ambiente
    application_root = os.environ.get('APPLICATION_ROOT', '').rstrip('/')
    if application_root:
        app.config['APPLICATION_ROOT'] = application_root
        
        # Configurar ProxyFix para funcionar corretamente com proxy reverso
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1
        )

    from flask_cors import CORS
    CORS(app)

    from datetime import timedelta
    from flask_jwt_extended import JWTManager
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    oauth.init_app(app)

    from app import models
    
    from flask_login import LoginManager
    login = LoginManager(app)
    login.login_view = 'auth.login'

    @login.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
