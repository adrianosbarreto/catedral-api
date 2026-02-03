from app import create_app, db
from app.models import User

app = create_app()

print("\n--- REGISTERED ROUTES ---")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.methods} {rule.rule}")
print("-------------------------\n")
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'app': app}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
