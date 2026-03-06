from app import create_app, db
from app.models import User, Membro

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Usuários no sistema:")
    for u in users:
        membro_nome = u.membro.nome if u.membro else "SEM VÍNCULO"
        print(f"- ID: {u.id} | Username: {u.username} | Role: {u.role} | Membro: {membro_nome}")
