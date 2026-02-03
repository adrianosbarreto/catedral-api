from app import create_app
from app.models import Ide

app = create_app()
with app.app_context():
    ides = Ide.query.all()
    print(f"Total IDEs: {len(ides)}")
    for ide in ides:
        print(f"ID: {ide.id}, Nome: {ide.nome}")
