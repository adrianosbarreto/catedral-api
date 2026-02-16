from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='jessica@jessica.com').first()
    if user:
        print(f"User: {user.username}")
        print(f"Role: '{user.role}'")
        print(f"Role Length: {len(user.role)}")
    else:
        print("User Jessica not found")
