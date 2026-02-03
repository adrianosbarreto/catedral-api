from app import create_app, db
from app.models import Membro, PapelMembro
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("--- Estado Civil ---")
    distinct_status = db.session.query(Membro.estado_civil).distinct().all()
    for status in distinct_status:
        print(f"'{status[0]}'")

    print("\n--- Papeis ---")
    distinct_roles = db.session.query(PapelMembro.papel).distinct().all()
    for role in distinct_roles:
        print(f"'{role[0]}'")
