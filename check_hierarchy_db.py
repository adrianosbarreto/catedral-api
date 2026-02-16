from app import create_app, db
from app.models import Membro

app = create_app()
with app.app_context():
    m = Membro.query.get(20) # Supervisor
    if m:
        print(f"Membro ID 20: {m.nome}")
        print(f"  IDE ID: {m.ide_id}")
        print(f"  Lider ID: {m.lider_id}")
        print(f"  Supervisor ID: {m.supervisor_id}")
        print(f"  Pastor ID: {m.pastor_id}")
        
        if m.lider: print(f"  Lider Nome: {m.lider.nome}")
        if m.supervisor: print(f"  Supervisor Nome: {m.supervisor.nome}")
        if m.pastor_id_rel: print(f"  Pastor Nome: {m.pastor_id_rel.nome}")
    else:
        print("Membro 20 not found")
