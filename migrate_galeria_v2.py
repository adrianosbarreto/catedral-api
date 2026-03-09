
from app import create_app, db
from sqlalchemy import text
import os

app = create_app('production') # or 'default'
with app.app_context():
    print("Iniciando migração da tabela 'projetos'...")
    try:
        # Check if table exists and column exists
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('projetos')]
        
        if 'galeria' not in columns:
            print("Adicionando coluna 'galeria'...")
            # Use text() for raw SQL
            db.session.execute(text("ALTER TABLE projetos ADD COLUMN galeria JSON DEFAULT '[]'"))
            db.session.commit()
            print("Coluna 'galeria' adicionada com sucesso!")
        else:
            print("Coluna 'galeria' já existe.")
            
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao migrar: {e}")
