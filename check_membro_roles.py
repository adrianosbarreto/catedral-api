from app import create_app, db
from app.models import User, PapelMembro

app = create_app()
with app.app_context():
    membro_id = 20 # Supervisor Member ID
    papeis = PapelMembro.query.filter_by(membro_id=membro_id).all()
    print(f"Roles for Membro ID {membro_id}:")
    for p in papeis:
        print(f"- {p.papel} (Role ID: {p.role_id})")
    
    user = User.query.filter_by(membro_id=membro_id).first()
    if user:
        print(f"User Role Property: {user.role}")
