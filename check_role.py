from app import create_app, db
from app.models import User, PapelMembro, Membro

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"{'Username':<30} {'ID':<5} {'Role':<15} {'MembroID'}")
    print("-" * 60)
    for u in users:
        if 'supervisor' in u.username or 'jessica' in u.username:
            print(f"({u.username})".ljust(30) + f"{u.id:<5} Role:{u.role:<15} MembroID:{u.membro_id if u.membro_id else 'N/A'}")
