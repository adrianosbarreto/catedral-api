
from app import create_app, db
from sqlalchemy import inspect

app = create_app('development')

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in DB:", tables)
