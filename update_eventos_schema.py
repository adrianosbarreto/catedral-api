from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Iniciando migração da tabela eventos...")
        
        # Migração da tabela eventos
        columns_eventos = [
            ("imagem_banner", "VARCHAR(500)"),
            ("criado_por_id", "INTEGER"),
            ("cta_texto", "VARCHAR(50)"),
            ("cta_link", "VARCHAR(500)"),
            ("ide_id", "INTEGER"),
            ("config_mensagem_antecedencia", "INTEGER DEFAULT 0"),
            ("ativo", "BOOLEAN DEFAULT TRUE"),
            ("gerenciar_participantes", "BOOLEAN DEFAULT FALSE"),
            ("instrucoes_inscricao", "TEXT"),
            ("valor_inscricao", "FLOAT"),
            ("exibir_vagas_restantes", "BOOLEAN DEFAULT FALSE"),
            ("perguntas", "JSONB DEFAULT '[]'::jsonb")
        ]
        
        inspector = db.inspect(db.engine)
        existing_columns_eventos = [c['name'] for c in inspector.get_columns('eventos')]
        
        for col_name, col_type in columns_eventos:
            if col_name not in existing_columns_eventos:
                print(f"Adicionando coluna {col_name} na tabela eventos...")
                try:
                    db.session.execute(text(f"ALTER TABLE eventos ADD COLUMN {col_name} {col_type}"))
                    print(f"Coluna {col_name} adicionada com sucesso.")
                except Exception as e:
                    print(f"Erro ao adicionar coluna {col_name}: {e}")
            else:
                print(f"Coluna {col_name} já existe na tabela eventos.")

        # Migração da tabela inscricoes_eventos
        columns_inscricoes = [
            ("respostas", "JSONB DEFAULT '{}'::jsonb")
        ]
        
        if 'inscricoes_eventos' not in inspector.get_table_names():
            print("Criando tabela inscricoes_eventos...")
            try:
                db.session.execute(text("""
                    CREATE TABLE inscricoes_eventos (
                        id SERIAL PRIMARY KEY,
                        evento_id INTEGER NOT NULL REFERENCES eventos(id),
                        membro_id INTEGER REFERENCES membros(id),
                        nome_externo VARCHAR(100),
                        email_externo VARCHAR(120),
                        telefone_externo VARCHAR(20),
                        status VARCHAR(20) DEFAULT 'pendente',
                        pago BOOLEAN DEFAULT FALSE,
                        data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        respostas JSONB DEFAULT '{}'::jsonb
                    )
                """))
                print("Tabela inscricoes_eventos criada com sucesso.")
            except Exception as e:
                print(f"Erro ao criar tabela inscricoes_eventos: {e}")
        else:
            existing_columns_inscricoes = [c['name'] for c in inspector.get_columns('inscricoes_eventos')]
            for col_name, col_type in columns_inscricoes:
                if col_name not in existing_columns_inscricoes:
                    print(f"Adicionando coluna {col_name} na tabela inscricoes_eventos...")
                    try:
                        db.session.execute(text(f"ALTER TABLE inscricoes_eventos ADD COLUMN {col_name} {col_type}"))
                        print(f"Coluna {col_name} adicionada com sucesso.")
                    except Exception as e:
                        print(f"Erro ao adicionar coluna {col_name}: {e}")
                else:
                    print(f"Coluna {col_name} já existe na tabela inscricoes_eventos.")

        if 'evento_ides' not in inspector.get_table_names():
            print("Criando tabela evento_ides...")
            try:
                db.session.execute(text("""
                    CREATE TABLE evento_ides (
                        evento_id INTEGER NOT NULL, 
                        ide_id INTEGER NOT NULL, 
                        PRIMARY KEY (evento_id, ide_id), 
                        FOREIGN KEY(evento_id) REFERENCES eventos (id), 
                        FOREIGN KEY(ide_id) REFERENCES ides (id)
                    )
                """))
                print("Tabela evento_ides criada com sucesso.")
            except Exception as e:
                print(f"Erro ao criar tabela evento_ides: {e}")
        else:
            print("Tabela evento_ides já existe.")
        
        db.session.commit()
        print("Migração concluída.")

if __name__ == "__main__":
    migrate()
