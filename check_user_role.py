
from app import create_app, db
from app.models import User, Membro, PapelMembro

app = create_app()
with app.app_context():
    print("Checking all users and their roles...")
    users = User.query.all()
    for u in users:
        print(f"User: {u.username} (ID: {u.id})")
        print(f"  Email: {u.email}")
        print(f"  Membro ID: {u.membro_id}")
        if u.membro:
            print(f"  Membro Name: {u.membro.nome}")
            roles = [p.papel for p in u.membro.papeis.all()]
            print(f"  Membro Roles: {roles}")
        print(f"  Property u.role: {u.role}")
        print("-" * 20)
