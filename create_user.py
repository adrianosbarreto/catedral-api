
from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    # Check if admin exists
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        user = User(username='admin', email='admin@example.com')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
