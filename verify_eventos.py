
import requests
from datetime import datetime, timedelta

base_url = 'http://127.0.0.1:5000'

# Login
def get_token():
    print("Logging in...")
    resp = requests.post(f"{base_url}/auth/login", json={'username': 'admin', 'password': 'admin123'})
    if resp.status_code == 200:
        return resp.json()['access_token']
    else:
        print("Login failed")
        return None

token = get_token()
headers = {'Authorization': f'Bearer {token}'}

if token:
    # 1. Create Evento
    print("\nCreating Evento...")
    new_event = {
        'titulo': 'Culto de Domingo',
        'data_inicio': (datetime.now() + timedelta(days=1)).isoformat(),
        'data_fim': (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        'local': 'Templo Principal',
        'tipo_evento': 'Culto',
        'capacidade_maxima': 100
    }
    r = requests.post(f"{base_url}/api/eventos", json=new_event, headers=headers)
    print(f"Create Status: {r.status_code}")
    if r.status_code == 201:
        evt_id = r.json()['id']
        print(f"Created ID: {evt_id}")
        
        # 2. List Eventos
        print("\nListing Eventos...")
        r = requests.get(f"{base_url}/api/eventos", headers=headers)
        print(f"List Count: {len(r.json())}")
        
        # 3. Get Evento
        print("\nGetting Evento...")
        r = requests.get(f"{base_url}/api/eventos/{evt_id}", headers=headers)
        print(f"Get Title: {r.json().get('titulo')}")
        
        # 4. Update Evento
        print("\nUpdating Evento...")
        r = requests.put(f"{base_url}/api/eventos/{evt_id}", json={'titulo': 'Culto da Família'}, headers=headers)
        print(f"Update Status: {r.status_code}")
        
        # 5. Delete Evento
        print("\nDeleting Evento...")
        r = requests.delete(f"{base_url}/api/eventos/{evt_id}", headers=headers)
        print(f"Delete Status: {r.status_code}")
        
    else:
        print(f"Create Failed: {r.text}")
