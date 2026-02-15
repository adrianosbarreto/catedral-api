import os
from app import create_app, db
from app.models import User, Membro

app = create_app()
with app.app_context():
    print("=== AUDITORIA DE USUÁRIOS ===")
    users = User.query.order_by(User.id).all()
    for u in users:
        m = u.membro
        membro_info = f"ID: {m.id} | Nome: {m.nome}" if m else "SEM MEMBRO"
        print(f"USER ID: {u.id} | Username: {u.username} | Email: {u.email} | Membro -> {membro_info}")

    print("\n=== AUDITORIA DE MEMBROS ===")
    membros = Membro.query.order_by(Membro.id).all()
    for mb in membros:
        u = User.query.filter_by(membro_id=mb.id).first()
        user_info = f"ID: {u.id} | Email: {u.email}" if u else "SEM USUÁRIO"
        print(f"MEMBRO ID: {mb.id} | Nome: {mb.nome} | User -> {user_info}")
