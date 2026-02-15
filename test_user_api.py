import os
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    email = 'adriano.sbarreto@hotmail.com'
    user = User.query.filter_by(email=email).first()
    if user:
        nome = user.membro.nome if user.membro else user.username
        print(f"USER DATA FOR {email}:")
        print(f"ID: {user.id}")
        print(f"Nome calculado: {nome}")
        print(f"Membro ID: {user.membro_id}")
        if user.membro:
             print(f"Membro Nome: {user.membro.nome}")
    else:
        print(f"User {email} not found")
