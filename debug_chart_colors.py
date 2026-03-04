
from app import create_app, db
from app.models import Ide, Celula, Membro
from sqlalchemy import func

def debug_stats():
    app = create_app()
    with app.app_context():
        print("--- IDEs and Colors ---")
        ides = Ide.query.all()
        for i in ides:
            print(f"IDE: {i.nome}, Cor: {i.cor}")
            
        print("\n--- Supervisor Stats (Internal Query) ---")
        supervisor_stats = db.session.query(
            Membro.nome.label('supervisor_nome'),
            Ide.cor.label('ide_cor'),
            func.count(Celula.id).label('quantidade')
        ).select_from(Celula)\
         .join(Membro, Celula.supervisor_id == Membro.id)\
         .join(Ide, Celula.ide_id == Ide.id)\
         .group_by(Membro.id, Membro.nome, Ide.cor).all()
         
        for row in supervisor_stats:
            print(f"Supervisor: {row[0]}, Cor: {row[1]}, Quantidade: {row[2]}")

if __name__ == '__main__':
    debug_stats()
