from app import create_app, db
from app.models import Celula, Membro

app = create_app()
with app.app_context():
    jessica = Membro.query.filter_by(email='jessica@jessica.com').first()
    if jessica:
        cells = Celula.query.filter_by(lider_id=jessica.id).all()
        print(f"Cells for Jessica (ID: {jessica.id}): {len(cells)}")
        for c in cells:
            print(f"- ID: {c.id}, Nome: {c.nome}, Ativo: {c.ativo}")
    else:
        print("Jessica not found")
