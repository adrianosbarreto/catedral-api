
import requests
import json
import sys

BASE_URL = 'http://localhost:5000/api'
AUTH_URL = 'http://localhost:5000/auth/login'

def login(username, password='admin123'):
    try:
        response = requests.post(AUTH_URL, json={
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

def check_admin_access():
    print("--- Testing Admin Access ---")
    token = login('admin')
    if not token:
        print("Could not login as admin. Check if server is running and admin user exists.")
        return

    headers = {'Authorization': f'Bearer {token}'}
    
    # Check Celulas
    resp_celulas = requests.get(f'{BASE_URL}/celulas', headers=headers)
    if resp_celulas.status_code == 200:
        celulas = resp_celulas.json()
        print(f"Admin can see {len(celulas)} celulas.")
    else:
        print(f"Error fetching celulas: {resp_celulas.status_code} - {resp_celulas.text}")

    # Check Membros
    resp_membros = requests.get(f'{BASE_URL}/membros', headers=headers)
    if resp_membros.status_code == 200:
        membros_data = resp_membros.json()
        print(f"Admin can see {membros_data.get('total', 0)} membros.")
    else:
        print(f"Error fetching membros: {resp_membros.status_code} - {resp_membros.text}")

if __name__ == "__main__":
    check_admin_access()
