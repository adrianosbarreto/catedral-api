"""
Script de teste rápido para verificar rotas do Flask
"""
from app import create_app
import os

# Testar com e sem APPLICATION_ROOT
configs = [
    ("Sem APPLICATION_ROOT", None),
    ("Com APPLICATION_ROOT=/catedral", "/catedral"),
]

for name, app_root in configs:
    print("=" * 70)
    print(f"🧪 TESTE: {name}")
    print("=" * 70)
    
    # Configurar ambiente
    if app_root:
        os.environ['APPLICATION_ROOT'] = app_root
    elif 'APPLICATION_ROOT' in os.environ:
        del os.environ['APPLICATION_ROOT']
    
    try:
        app = create_app('production')
        
        print(f"\n✅ App criada com sucesso")
        print(f"   APPLICATION_ROOT: {app.config.get('APPLICATION_ROOT', 'Não definido')}")
        
        # Listar rotas
        print(f"\n📋 Rotas registradas:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                print(f"   {rule.endpoint:30} {str(rule.methods):30} {rule.rule}")
        
        # Testar requisição
        print(f"\n🔍 Testando requisições:")
        with app.test_client() as client:
            # Testar raiz
            resp = client.get('/')
            print(f"   GET / → {resp.status_code}")
            
            # Testar /catedral se configurado
            if app_root:
                resp = client.get('/catedral/')
                print(f"   GET /catedral/ → {resp.status_code}")
                
                resp = client.get('/catedral/api/')
                print(f"   GET /catedral/api/ → {resp.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
    
    print()

print("=" * 70)
print("💡 DIAGNÓSTICO")
print("=" * 70)
print()
print("Se as rotas aparecem SEM /catedral no prefixo:")
print("  ➜ O APPLICATION_ROOT não está afetando o url_map")
print("  ➜ As rotas são: /, /api/, /auth/, etc.")
print("  ➜ O nginx deve fazer proxy_pass para http://localhost:5000/")
print("  ➜ E usar rewrite para remover /catedral antes de passar ao Flask")
print()
print("Se as rotas aparecem COM /catedral no prefixo:")
print("  ➜ O APPLICATION_ROOT está funcionando")
print("  ➜ As rotas são: /catedral/, /catedral/api/, etc.")
print("  ➜ O nginx deve fazer proxy_pass http://localhost:5000")
print()
