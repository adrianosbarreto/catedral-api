from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Adicionar coluna 'ativo' na tabela 'celulas'
    try:
        db.session.execute(text("ALTER TABLE celulas ADD COLUMN ativo BOOLEAN DEFAULT TRUE"))
        db.session.commit()
        print("Column 'ativo' added to 'celulas' successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'ativo' in 'celulas' might already exist or error: {e}")

    # Adicionar coluna 'ativo' na tabela 'membros'
    try:
        db.session.execute(text("ALTER TABLE membros ADD COLUMN ativo BOOLEAN DEFAULT TRUE"))
        db.session.commit()
        print("Column 'ativo' added to 'membros' successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'ativo' in 'membros' might already exist or error: {e}")

    print("Database update complete.")
