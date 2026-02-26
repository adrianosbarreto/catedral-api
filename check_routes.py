from app import create_app

app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'notifications' in rule.rule:
            print(f"Rule: {rule.rule} Methods: {rule.methods}")
