from app import create_app, db
import os

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Database has been reset with the new schema.')
