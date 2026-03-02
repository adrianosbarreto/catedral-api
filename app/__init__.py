from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()

from flask_apscheduler import APScheduler
scheduler = APScheduler()

def setup_ssh_tunnel(app):
    """Configura e inicia um túnel SSH se necessário."""
    if os.environ.get('SSH_TUNNEL_ENABLED', 'false').lower() != 'true':
        return None

    try:
        from sshtunnel import SSHTunnelForwarder
        import logging
        
        ssh_host = os.environ.get('SSH_HOST')
        ssh_port = int(os.environ.get('SSH_PORT', 22))
        ssh_user = os.environ.get('SSH_USER')
        ssh_password = os.environ.get('SSH_PASSWORD')
        ssh_pkey = os.environ.get('SSH_PKEY_PATH')
        
        remote_db_host = os.environ.get('DB_REMOTE_HOST', '127.0.0.1')
        remote_db_port = int(os.environ.get('DB_REMOTE_PORT', 5432))

        print(f"🔗 [SSH] Iniciando túnel para {ssh_host}:{ssh_port}...")
        
        tunnel_kwargs = {
            'ssh_address_or_host': (ssh_host, ssh_port),
            'ssh_username': ssh_user,
            'remote_bind_address': (remote_db_host, remote_db_port),
        }
        
        if ssh_pkey and os.path.exists(ssh_pkey):
            tunnel_kwargs['ssh_pkey'] = ssh_pkey
        elif ssh_password:
            tunnel_kwargs['ssh_password'] = ssh_password

        tunnel = SSHTunnelForwarder(**tunnel_kwargs)
        tunnel.start()
        
        # Atualiza a URL do banco para apontar para o túnel local
        local_port = tunnel.local_bind_port
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Substitui o host e porta na URL (assume formato postgresql://user:pass@host:port/db)
        import re
        new_db_url = re.sub(r'@[\w\.-]+(:\d+)?/', f'@127.0.0.1:{local_port}/', db_url)
        app.config['SQLALCHEMY_DATABASE_URI'] = new_db_url
        
        print(f"✅ [SSH] Túnel estabelecido na porta local {local_port}")
        
        return tunnel
    except Exception as e:
        print(f"❌ [SSH] Erro ao criar túnel: {e}")
        return None

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configurar subpath usando DispatcherMiddleware se definido no ambiente
    subpath = os.environ.get('APPLICATION_SUBPATH', '').rstrip('/')
    if subpath:
        print(f"🔧 [DEBUG] Ativando subpath: {subpath}")
        from werkzeug.middleware.dispatcher import DispatcherMiddleware
        from werkzeug.wrappers import Response
        
        # Aplicação dummy para a raiz (retorna 404)
        def simple_app(environ, start_response):
            print(f"🔧 [DEBUG] Request na raiz (fora do subpath): {environ.get('PATH_INFO')}")
            response = Response('Not Found', status=404)
            return response(environ, start_response)
        
        # Montar a aplicação Flask no subpath
        app.wsgi_app = DispatcherMiddleware(simple_app, {
            subpath: app.wsgi_app
        })
        print(f"🔧 [DEBUG] DispatcherMiddleware configurado em {subpath}")
    else:
        print("🔧 [DEBUG] Subpath não definido, servindo na raiz (/)")

    from flask_cors import CORS
    # Permitir origens específicas ou todas (mais seguro para produção com subdomains variados)
    # Adicionado suporte para acesso via IP local para testes em dispositivos móveis
    CORS(app, resources={r"/*": {
        "origins": [
            "https://www.liderfoursquare.com.br", 
            "https://liderfoursquare.com.br",
            "http://www.liderfoursquare.com.br",
            "http://liderfoursquare.com.br",
            "http://localhost:5173", 
            "http://localhost:8080",
            "*" # Allow all for local testing convenience
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"]
    }})

    from datetime import timedelta
    from flask_jwt_extended import JWTManager
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    jwt = JWTManager(app)

    # Configurar Túnel SSH se estiver em desenvolvimento
    app.ssh_tunnel = setup_ssh_tunnel(app)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    oauth.init_app(app)

    # Initialize APScheduler
    scheduler.init_app(app)
    scheduler.start()

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
