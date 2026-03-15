
from app import db, create_app
from app.models import User, Role, PapelMembro, Membro

app = create_app('production')
with app.app_context():
    # Find one pastor_de_rede
    user = User.query.join(Membro).join(PapelMembro).join(Role).filter(Role.name == 'pastor_de_rede').first()
    if not user:
        # Try deprecated papel column
        user = User.query.join(Membro).join(PapelMembro).filter(PapelMembro.papel == 'pastor_de_rede').first()
    
    if user:
        print(f"Found Pastor de Rede: {user.username}")
    else:
        print("No Pastor de Rede found.")
