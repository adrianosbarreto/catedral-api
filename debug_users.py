import os
from app import create_app, db
from app.models import User, Membro

app = create_app()
with app.app_context():
    print("--- USUÁRIOS E MEMBROS ---")
    users = User.query.all()
    for u in users:
        membro_nome = u.membro.nome if u.membro else "SEM MEMBRO VINCULADO"
        print(f"User ID: {u.id} | Username: {u.username} | Email: {u.email} | Membro: {membro_nome}")
    
    print("\n--- MEMBROS SEM USUÁRIO ---")
    membros_sem_user = Membro.query.filter(~Membro.user.has()).all()
    for m in membros_sem_user:
        print(f"Membro ID: {m.id} | Nome: {m.nome} | Email: {m.email}")
