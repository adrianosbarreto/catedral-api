import os
import sys
from sqlalchemy import text
from app import create_app, db

app = create_app('production')
with app.app_context():
    print("Conectando ao banco...")
    try:
        # Tenta alterar as colunas para TEXT no postgres (e SQLite se suportado, mas SQLite já não limita tamanho assim)
        # Suporta se for SQLite ou Postgres.
        engine = db.engine
        
        if engine.name == 'postgresql':
            print("Executando ALTER COLUMN para text no PostgreSQL...")
            db.session.execute(text("ALTER TABLE eventos ALTER COLUMN imagem_banner TYPE text;"))
            try:
                db.session.execute(text("ALTER TABLE noticias ALTER COLUMN foto_url TYPE text;"))
            except Exception as e:
                print(f"Erro na tabela noticias (talvez não exista ou nome diferente): {e}")
            db.session.commit()
            print("Alterado para TEXT com sucesso no PostgreSQL.")
        else:
            print("Banco de dados não é PostgreSQL (SQLite não exige alteração para TEXT/String de forma estrita ou requer workaround, prosseguindo...).")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao alterar schema: {e}")
