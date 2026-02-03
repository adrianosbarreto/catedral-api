
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def login(username, password='123456'):
    try:
        response = requests.post(f'http://localhost:5000/auth/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"Login failed for {username}: {response.text}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def check_celulas(username, role_name):
    print(f"\n--- Checking visibility for {role_name} ({username}) ---")
    token = login(username)
    if not token: return

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/celulas', headers=headers)
    
    if response.status_code == 200:
        celulas = response.json()
        print(f"Found {len(celulas)} celulas.")
        for c in celulas:
            print(f"  - {c['nome']} (Rede: {c['ide_id']})")
    else:
        print(f"Error fetching celulas: {response.text}")

if __name__ == "__main__":
    # 1. Pastor Geral (Should see all)
    check_celulas('pastor_geral', 'Pastor Geral')
    
    # 2. Pastor Rede A (Should see Rede A cells)
    check_celulas('pastor_rede_a', 'Pastor Rede A')
    
    # 3. Pastor Rede B (Should see Rede B cells)
    check_celulas('pastor_rede_b', 'Pastor Rede B')
    
    # 4. Supervisor A1 (Should see cells supervised by him)
    check_celulas('sup_a1', 'Supervisor A1 (Rede A)')
    
    # 5. Leader A1-1 (Should see own cell)
    check_celulas('lider_a1_1', 'Leader A1-1')

    # 6. Leader B1-1 (Should see own cell)
    check_celulas('lider_b1_1', 'Leader B1-1')
