
from app import create_app, db
from app.models import Celula

app = create_app('production')
with app.app_context():
    q = Celula.query.filter_by(ativo=True)
    total = q.count()
    with_coords = q.filter(Celula.latitude.isnot(None), Celula.longitude.isnot(None)).count()
    print(f"Total Active Cells: {total}")
    print(f"Cells with Coordinates: {with_coords}")
    print(f"Cells missing Coordinates: {total - with_coords}")
