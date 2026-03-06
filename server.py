"""
Servidor de produção para o Igreja em Foco Backend
Utiliza Waitress como servidor WSGI para ambientes de produção
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from waitress import serve
from app import create_app

import logging

# Configurar logs do waitress para suprimir avisos de fila
logging.getLogger('waitress.queue').setLevel(logging.ERROR)

# Criar aplicação com configuração de produção
app = create_app('production')

if __name__ == '__main__':
    # Configurações do servidor
    host = os.environ.get('SERVER_HOST', '0.0.0.0')
    port = int(os.environ.get('SERVER_PORT', 5000))
    
    subpath = os.environ.get('APPLICATION_SUBPATH', '')
    url_completa = f"http://{host}:{port}{subpath}"
    
    print(f"\n{'='*60}")
    print(f"🚀 Igreja em Foco Backend - Servidor de Produção")
    print(f"{'='*60}")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🌐 URL Base: {url_completa}")
    print(f"🔑 Admin: admin / admin123")
    print(f"{'='*60}\n")
    
    # Iniciar servidor Waitress
    serve(
        app,
        host=host,
        port=port,
        threads=4,  # Número de threads para processar requisições
        url_scheme='http',
        _quiet=False
    )
