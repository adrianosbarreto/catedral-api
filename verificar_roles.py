"""
Verificar roles no banco
"""
from app import create_app, db
from app.models import Role, User

def verificar_roles():
    app = create_app()
    with app.app_context():
        print("🔍 Verificando roles...")
        
        roles = Role.query.all()
        print(f"Total de roles: {len(roles)}")
        
        for role in roles:
            print(f"  - {role.name} ({role.label})")
        
        print("\n🔍 Verificando user.role do admin...")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"  Admin role: '{admin.role}'")
            
            # Tentar buscar role
            role_obj = Role.query.filter_by(name=admin.role).first()
            if role_obj:
                print(f"  ✅ Role encontrada: {role_obj.label}")
            else:
                print(f"  ❌ Role '{admin.role}' não existe no banco!")
                print(f"  💡 Isso causa erro 500 no login!")

if __name__ == '__main__':
    verificar_roles()
