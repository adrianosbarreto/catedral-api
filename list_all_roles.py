
from app import db, create_app
from app.models import User, Role, PapelMembro

app = create_app('production')
with app.app_context():
    users = User.query.all()
    print("User Roles:")
    for u in users:
        print(f"Username: {u.username}, Role: {u.role}")
