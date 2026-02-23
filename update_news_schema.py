
from app import create_app, db
from app.models import Noticia

app = create_app('development')
with app.app_context():
    try:
        db.create_all()
        print("Tabelas atualizadas com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar tabelas: {e}")
