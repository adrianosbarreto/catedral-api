from app import create_app, db
from app.models import Membro, Ide, Celula, Endereco, PapelMembro

app = create_app()

with app.app_context():
    print("Iniciando limpeza do banco de dados...")
    
    try:
        # 1. Limpar referências circulares
        db.session.query(Membro).update({Membro.lider_id: None})
        db.session.query(Ide).update({Ide.pastor_id: None})
        db.session.commit()
        
        # 2. Deletar Celulas (dependem de User/Membro)
        num_celulas = Celula.query.delete()
        print(f"Deletadas {num_celulas} células.")
        
        # 3. Deletar Membros (cascateará para enderecos e papeis)
        num_membros = Membro.query.delete()
        print(f"Deletados {num_membros} membros.")
        
        # 4. Deletar IDEs
        num_ides = Ide.query.delete()
        print(f"Deletadas {num_ides} IDEs.")
        
        db.session.commit()
        print("Limpeza concluída com sucesso!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro durante a limpeza: {e}")
