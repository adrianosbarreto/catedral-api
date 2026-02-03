
import sys
import os

print(f"CWD: {os.getcwd()}")
sys.path.insert(0, os.getcwd())
print(f"SYS.PATH: {sys.path}")

try:
    from app import create_app
    print("SUCCESS: create_app imported")
    app = create_app('development')
    print("SUCCESS: app created")
except ImportError as e:
    print(f"FAILURE IMPORT: {e}")
except Exception as e:
    print(f"FAILURE OTHER: {e}")
