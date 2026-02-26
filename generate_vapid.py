import json
from pywebpush import generate_vapid_keypair
import os

keypair = generate_vapid_keypair()
print("VAPID_PRIVATE_KEY=" + keypair["private_key"])
print("VAPID_PUBLIC_KEY=" + keypair["public_key"])

# Let's save them to .env
env_lines = []
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        env_lines = f.readlines()

has_private = False
has_public = False
for i, line in enumerate(env_lines):
    if line.startswith('VAPID_PRIVATE_KEY='):
        env_lines[i] = "VAPID_PRIVATE_KEY=" + keypair["private_key"] + "\n"
        has_private = True
    elif line.startswith('VAPID_PUBLIC_KEY='):
        env_lines[i] = "VAPID_PUBLIC_KEY=" + keypair["public_key"] + "\n"
        has_public = True

if not has_private:
    env_lines.append("\nVAPID_PRIVATE_KEY=" + keypair["private_key"] + "\n")
if not has_public:
    env_lines.append("VAPID_PUBLIC_KEY=" + keypair["public_key"] + "\n")

with open('.env', 'w') as f:
    f.writelines(env_lines)
