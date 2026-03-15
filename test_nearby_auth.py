
import requests
from app import create_app, db
from app.models import User
from flask_jwt_extended import create_access_token

app = create_app('production')
with app.app_context():
    user = User.query.filter_by(username='diego@diego.com').first()
    if not user:
        print("User diego@diego.com not found")
        exit(1)
    
    token = create_access_token(identity=str(user.id))
    print(f"Token generated for {user.username}")

def test_endpoint(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        print(f"Testing {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {len(data)} cells found")
            for cell in data[:3]:
                print(f" - Cell: {cell['nome']}, IDE: {cell.get('ide', {}).get('nome')}, Distance: {cell.get('distance')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

url = "http://localhost:5000/catedral/api/celulas/nearby?lat=-1.4716302&lng=-48.4910653&radius=50"
test_endpoint(url, token)
