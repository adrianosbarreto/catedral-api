from app import create_app
from app.models import Nucleo, Celula, db

app = create_app('production')
with app.app_context():
    celula_id = 10
    nucleos = Nucleo.query.filter_by(celula_id=celula_id).all()
    print(f"Núcleos encontrados para a célula {celula_id}:")
    for n in nucleos:
        print(f"ID: {n.id} | Nome: {n.nome}")
    
    if not nucleos:
        print("Nenhum núcleo encontrado.")
