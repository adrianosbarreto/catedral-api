from app import create_app, db
from app.models import NotificationSubscription

app = create_app()
with app.app_context():
    subs = NotificationSubscription.query.all()
    print(f"Total de subscriptions: {len(subs)}")
    for sub in subs:
        print(f"ID: {sub.id}, User ID: {sub.user_id}, Endpoint: {sub.endpoint[:30]}...")
