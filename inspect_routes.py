
from app import create_app
import os

app = create_app('production')

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

subpath = os.environ.get('APPLICATION_SUBPATH', '')
print(f"\nAPPLICATION_SUBPATH: {subpath}")
