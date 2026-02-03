
import requests
import json

BASE_URL = 'http://localhost:5000/auth'

def check_user_role(username, password='123456'):
    print(f"--- Checking role for {username} ---")
    
    # 1. Login
    try:
        resp = requests.post(f'{BASE_URL}/login', json={'username': username, 'password': password})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return
        
        data = resp.json()
        print("Login Response User Data:")
        print(json.dumps(data.get('user'), indent=2))
        
        token = data['access_token']
        role_in_login = data.get('user', {}).get('role')
        print(f"Role in Login: '{role_in_login}' (Type: {type(role_in_login)})")

        # 2. Get Me
        headers = {'Authorization': f'Bearer {token}'}
        resp_me = requests.get(f'{BASE_URL}/me', headers=headers)
        if resp_me.status_code != 200:
            print(f"Get Me failed: {resp_me.status_code} - {resp_me.text}")
            return

        data_me = resp_me.json()
        print("Get Me Response User Data:")
        print(json.dumps(data_me.get('user'), indent=2))
        
        role_in_me = data_me.get('user', {}).get('role')
        print(f"Role in Me: '{role_in_me}' (Type: {type(role_in_me)})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_role('pastor_rede_a')
