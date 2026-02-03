from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE papeis_membros ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
            print("Column role_id added.")
        except Exception as e:
            print(f"Error adding column (maybe exists): {e}")

        # SQLite doesn't strictly enforce FK by default unless PRAGMA foreign_keys=ON is set, 
        # but the schema definition is good for documentation.
