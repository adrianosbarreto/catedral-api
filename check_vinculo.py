from app import create_app
from app.models import MembroNucleo, Membro, db

app = create_app('production')
with app.app_context():
    membro_id = 26
    vinculos = MembroNucleo.query.filter_by(membro_id=membro_id).all()
    print(f"Vínculos encontrados para o membro ID {membro_id}:")
    for v in vinculos:
        print(f"ID Vínculo: {v.id} | Núcleo ID: {v.nucleo_id} | Convidado: {v.is_convidado}")
    
    if not vinculos:
        print("Nenhum vínculo encontrado.")
