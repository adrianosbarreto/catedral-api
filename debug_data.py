from app import create_app
from app.models import Celula, Ide, db

app = create_app('production')
with app.app_context():
    print(f"{'ID':<5} | {'Nome Célula':<25} | {'IDE ID':<6} | {'Pastor ID (IDE)':<15}")
    print("-" * 60)
    celulas = Celula.query.filter_by(ativo=True).limit(10).all()
    for c in celulas:
        pastor_id = c.ide.pastor_id if c.ide else "N/A"
        print(f"{c.id:<5} | {c.nome:<25} | {c.ide_id:<6} | {pastor_id:<15}")

    print("\n" + "="*60 + "\n")
    print(f"{'ID':<5} | {'Nome IDE':<25} | {'Pastor ID':<10} | {'Pastor Nome':<20}")
    print("-" * 60)
    ides = Ide.query.all()
    for ide in ides:
        pastor_nome = ide.pastor.nome if ide.pastor else "Nenhum"
        print(f"{ide.id:<5} | {ide.nome:<25} | {str(ide.pastor_id):<10} | {pastor_nome:<20}")
