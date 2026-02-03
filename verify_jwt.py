
import requests

base_url = 'http://127.0.0.1:5000'

def check(url, method='GET', json=None):
    print(f"Checking {method} {url}...")
    try:
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json=json)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
             print(f"Response: {response.text[:200]}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# Check root
check(base_url + '/')

# Check API
check(base_url + '/api/ides')

# Check Auth Login
login_url = base_url + '/auth/login'
credentials = {'username': 'admin', 'password': 'admin123'}
response = check(login_url, method='POST', json=credentials)

if response and response.status_code == 200:
    token = response.json().get('access_token')
    print("Token obtained.")
    
    # Check Me
    headers = {'Authorization': f'Bearer {token}'}
    print("Checking /auth/me...")
    r = requests.get(base_url + '/auth/me', headers=headers)
    print(f"Me Status: {r.status_code}")
    if r.status_code != 200:
        print(f"Me Response: {r.text}")
