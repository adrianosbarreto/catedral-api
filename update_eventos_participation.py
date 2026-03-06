from app import create_app, db
from sqlalchemy import text, inspect

def migrate():
    app = create_app()
    with app.app_context():
        print("Iniciando migração para Gestão de Participantes...")
        
        # 1. Adicionar novas colunas na tabela eventos
        columns_to_add = [
            ("gerenciar_participantes", "BOOLEAN DEFAULT FALSE"),
            ("instrucoes_inscricao", "TEXT"),
            ("valor_inscricao", "FLOAT"),
            ("exibir_vagas_restantes", "BOOLEAN DEFAULT FALSE")
        ]
        
        inspector = inspect(db.engine)
        existing_columns = [c['name'] for c in inspector.get_columns('eventos')]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adicionando coluna {col_name} na tabela eventos...")
                try:
                    db.session.execute(text(f"ALTER TABLE eventos ADD COLUMN {col_name} {col_type}"))
                    print(f"Coluna {col_name} adicionada com sucesso.")
                except Exception as e:
                    print(f"Erro ao adicionar coluna {col_name}: {e}")
            else:
                print(f"Coluna {col_name} já existe na tabela eventos.")
        
        # 2. Criar novas tabelas (evento_ides e inscricoes_eventos)
        # O create_all() criará apenas as tabelas que não existem
        print("Criando novas tabelas se não existirem...")
        try:
            db.create_all()
            print("Tabelas criadas/verificadas com sucesso.")
        except Exception as e:
            print(f"Erro ao criar novas tabelas: {e}")
            
        db.session.commit()
        print("Migração concluída com sucesso.")

if __name__ == "__main__":
    migrate()
