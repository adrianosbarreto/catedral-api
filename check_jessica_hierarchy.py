from app import create_app, db
from app.models import Membro

app = create_app()
with app.app_context():
    m = Membro.query.filter_by(email='jessica@jessica.com').first()
    if m:
        print(f"Membro Jessica: {m.nome} (ID: {m.id})")
        print(f"  IDE ID: {m.ide_id}")
        print(f"  Lider ID: {m.lider_id}")
        print(f"  Supervisor ID: {m.supervisor_id}")
        
        if m.lider: print(f"  Lider Nome: {m.lider.nome}")
        if m.supervisor: print(f"  Supervisor Nome: {m.supervisor.nome}")
    else:
        print("Membro Jessica not found")
