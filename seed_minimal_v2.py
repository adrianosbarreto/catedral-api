"""
Seed MINIMALISTA - Apenas dados essenciais
Para funcionar 100% com PostgreSQL
"""
from app import create_app, db
from app.models import User, Membro, Ide, Role

def seed_minimal():
    app = create_app()
    with app.app_context():
        print("🗑️  Limpando...")
        
        db.session.query(Membro).delete()
        db.session.query(Ide).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        print("✅ Limpo!")

        # 1. IDE sem pastor
        print("\n📍 Criando IDE...")
        ide = Ide(nome='IDE Sede')
        db.session.add(ide)
        db.session.commit()
        print(f"✅ IDE criada (ID: {ide.id})")

        # 2. Membro (Apenas campos obrigatórios)
        print("\n👥 Criando membro...")
        membro = Membro(
            nome='João Silva',
            ide_id=ide.id
        )
        db.session.add(membro)
        db.session.commit()
        print(f"✅ Membro criado (ID: {membro.id})")

        # 3. Atualizar IDE com pastor
        print("\n👨‍💼 Definindo pastor...")
        ide.pastor_id = membro.id
        db.session.commit()
        print("✅ Pastor definido")

        # 4. Usuário Admin
        print("\n👤 Criando admin...")
        admin = User(
            username='admin',
            email='admin@admin.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin criado")

        print("\n" + "="*50)
        print("✅ SEED CONCLUÍDO!")
        print("="*50)
        print(f"📍 IDE: {ide.nome} (ID: {ide.id})")
        print(f"👥 Membro: {membro.nome} (ID: {membro.id})")
        print(f"👤 Admin: admin / admin123")
        print("="*50)
        print("\n💡 Agora você pode criar mais dados pelo sistema!")

if __name__ == '__main__':
    seed_minimal()
