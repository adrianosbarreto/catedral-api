from app import create_app, db
from app.models import PapelMembro, Role

app = create_app()
with app.app_context():
    roles = {r.name: r.id for r in Role.query.all()}
    print(f"Available roles: {roles}")
    
    papeis = PapelMembro.query.filter(PapelMembro.role_id == None).all()
    print(f"Found {len(papeis)} roles to migrate")
    
    count = 0
    for p in papeis:
        if p.papel in roles:
            p.role_id = roles[p.papel]
            count += 1
        else:
            print(f"Role '{p.papel}' not found in roles table for member {p.membro_id}")
            
    db.session.commit()
    print(f"Successfully migrated {count} roles")
