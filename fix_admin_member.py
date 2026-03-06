from app import create_app, db
from app.models import User, Membro

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin and not admin.membro_id:
        print("Vinculando o usuário 'admin' a um perfil de membro...")
        membro = Membro.query.filter_by(nome='Administrador').first()
        if not membro:
            membro = Membro(nome='Administrador', email='admin@catedral.com', ativo=True)
            db.session.add(membro)
            db.session.flush()
        
        admin.membro_id = membro.id
        db.session.commit()
        print(f"✅ Usuário 'admin' vinculado ao membro ID {membro.id}")
    else:
        print("Usuário 'admin' já possui vínculo ou não foi encontrado.")
