import os
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    email = 'adriano.sbarreto@hotmail.com'
    users = User.query.filter((User.email == email) | (User.username == email)).all()
    print(f"--- USUÁRIOS ENCONTRADOS PARA {email} ---")
    for u in users:
        membro_nome = u.membro.nome if u.membro else "SEM MEMBRO"
        print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Membro: {membro_nome}")
