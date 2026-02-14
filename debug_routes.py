"""
Script para debugar as rotas e o subpath carregado na aplicação
"""
from app import create_app
import os
from dotenv import load_dotenv

def debug_app():
    load_dotenv()
    subpath = os.environ.get('APPLICATION_SUBPATH', 'NÃO DEFINIDO')
    print(f"🔍 DEBUG: APPLICATION_SUBPATH no ambiente: '{subpath}'")
    
    app = create_app('production')
    print(f"🔍 DEBUG: WSGI app type: {type(app.wsgi_app)}")
    
    print("\n📂 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  - {rule}")

if __name__ == '__main__':
    debug_app()
