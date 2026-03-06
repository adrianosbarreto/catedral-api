
from app import create_app, db
from app.models import Evento, User, Membro
from datetime import datetime
import traceback

def test_get_eventos():
    app = create_app()
    with app.app_context():
        print("--- Testando Query de Eventos ---")
        try:
            # Pegar um usuário que tenha membro associado
            user = User.query.join(Membro).first()
            if not user:
                user = User.query.first()
            
            if not user:
                print("Nenhum usuário encontrado no DB.")
                return

            print(f"Testando como usuário: {user.username} (Role: {user.role})")
            
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            print(f"Colunas em 'eventos': {[c['name'] for c in inspector.get_columns('eventos')]}")
            print(f"Tabelas no DB: {inspector.get_table_names()}")
            
            show_finished = True
            agora = datetime.utcnow()
            
            query = Evento.query
            if show_finished:
                query = query.filter(Evento.data_fim < agora)
            else:
                query = query.filter(Evento.ativo == True)
                query = query.filter(Evento.data_fim >= agora)
            
            # Aplicar filtro de visibilidade
            if user.role not in ['admin', 'pastor']:
                from sqlalchemy import or_
                user_ide_id = user.membro.ide_id if user.membro else None
                if user_ide_id:
                    query = query.filter(or_(
                        Evento.ide_id == None,
                        Evento.ide_id == user_ide_id,
                        ~Evento.ides.any(),
                        Evento.ides.any(id=user_ide_id)
                    ))
                else:
                    query = query.filter(or_(
                        Evento.ide_id == None,
                        ~Evento.ides.any()
                    ))
            
            print("Executando query...")
            eventos = query.order_by(Evento.data_inicio).all()
            print(f"Sucesso! {len(eventos)} eventos encontrados.")
            
            if eventos:
                print("Testando to_dict no primeiro evento...")
                print(eventos[0].to_dict())
                
        except Exception as e:
            print("\n!!! ERRO DETECTADO !!!")
            traceback.print_exc()

if __name__ == "__main__":
    test_get_eventos()
