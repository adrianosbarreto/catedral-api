"""
Testar login do admin
"""
from app import create_app, db
from app.models import User

def testar_login():
    app = create_app()
    with app.app_context():
        print("🔍 Testando login do admin...")
        
        # Buscar admin
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Admin não encontrado!")
            return
        
        print(f"✅ Admin encontrado: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password hash length: {len(admin.password_hash) if admin.password_hash else 0}")
        print(f"   Password hash: {admin.password_hash[:50]}..." if admin.password_hash else "None")
        
        # Testar senha
        senhas = ['admin123', 'Admin123', 'admin']
        
        for senha in senhas:
            resultado = admin.check_password(senha)
            print(f"\n   Senha '{senha}': {'✅ CORRETO' if resultado else '❌ INCORRETO'}")

if __name__ == '__main__':
    testar_login()
