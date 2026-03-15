
from app import create_app, db
from app.models import Role, User

app = create_app('production')
with app.app_context():
    print("Roles in DB:")
    for r in Role.query.all():
        print(f" - {r.name} ({r.label})")
    
    print("\nAdmins in DB:")
    for u in User.query.filter_by(role='admin').all():
        print(f" - {u.username}")
