
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(projetos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'galeria' not in columns:
            print("Adding 'galeria' column to 'projetos' table...")
            cursor.execute("ALTER TABLE projetos ADD COLUMN galeria JSON DEFAULT '[]'")
            conn.commit()
            print("Migration successful!")
        else:
            print("Column 'galeria' already exists.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
