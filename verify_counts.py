
from app import create_app, db
from app.models import Celula, Membro

app = create_app()
with app.app_context():
    cells_count = Celula.query.count()
    members_count = Membro.query.count()
    print(f"TOTAL_CELLS: {cells_count}")
    print(f"TOTAL_MEMBERS: {members_count}")
