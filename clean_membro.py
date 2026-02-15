from app import create_app, db
from app.models import Membro, User, PapelMembro, Endereco

def clean_duplicate():
    app = create_app('development')
    with app.app_context():
        # Membro a ser removido (duplicado)
        m_id = 6
        m = db.session.get(Membro, m_id)
        if m:
            print(f"Limpando dados do membro {m_id}: {m.nome}")
            
            # Deletar em ordem para respeitar FKs
            User.query.filter_by(membro_id=m_id).delete()
            PapelMembro.query.filter_by(membro_id=m_id).delete()
            Endereco.query.filter_by(membro_id=m_id).delete()
            
            db.session.delete(m)
            db.session.commit()
            print("Membro 6 removido com sucesso!")
        else:
            print("Membro 6 nao encontrado.")

if __name__ == "__main__":
    clean_duplicate()
