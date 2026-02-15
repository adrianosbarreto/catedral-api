from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 1. Create new tables
    db.create_all()
    
    # 2. Add columns to Membro if they don't exist
    # SQLite doesn't support IF NOT EXISTS in ALTER TABLE directly via SQLAlchemy common calls easily,
    # so we'll use raw SQL and try/except or check.
    
    try:
        db.session.execute(text("ALTER TABLE membros ADD COLUMN tipo VARCHAR(20) DEFAULT 'membro'"))
        db.session.commit()
        print("Column 'tipo' added successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'tipo' might already exist or error: {e}")

    try:
        db.session.execute(text("ALTER TABLE membros ADD COLUMN batizado BOOLEAN DEFAULT 0"))
        db.session.commit()
        print("Column 'batizado' added successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'batizado' might already exist or error: {e}")

    try:
        db.session.execute(text("ALTER TABLE membros ADD COLUMN supervisor_id INTEGER REFERENCES membros(id)"))
        db.session.commit()
        print("Column 'supervisor_id' added successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'supervisor_id' might already exist or error: {e}")

    try:
        db.session.execute(text("ALTER TABLE membros ADD COLUMN pastor_id INTEGER REFERENCES membros(id)"))
        db.session.commit()
        print("Column 'pastor_id' added successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Column 'pastor_id' might already exist or error: {e}")

    print("Database sync complete.")
