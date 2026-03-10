
from app import create_app, db
from sqlalchemy import text

app = create_app('development')

def add_columns():
    with app.app_context():
        try:
            # Adicionar pastor_destino_id
            db.session.execute(text("ALTER TABLE convites ADD COLUMN IF NOT EXISTS pastor_destino_id INTEGER REFERENCES membros(id)"))
            # Adicionar lider_destino_id
            db.session.execute(text("ALTER TABLE convites ADD COLUMN IF NOT EXISTS lider_destino_id INTEGER REFERENCES membros(id)"))
            db.session.commit()
            print("✅ Colunas pastor_destino_id e lider_destino_id adicionadas com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao adicionar colunas: {e}")

if __name__ == "__main__":
    add_columns()
