
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_invite_flow():
    # 1. Login as Admin
    print("Testing login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if login_resp.status_code != 200:
        print("Login failed:", login_resp.text)
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login success!")

    # 2. Generate Invite
    url = f"{BASE_URL}/auth/invite"
    print(f"\nGenerating invite at {url}...")
    gen_resp = requests.post(url, json={"ide_id": 1}, headers=headers)
    if gen_resp.status_code != 201:
        print("Invite generation failed:", gen_resp.text)
        return
    
    invite_token = gen_resp.json()["token"]
    print(f"Invite generated! Token: {invite_token}")

    # 3. Validate Invite
    print("\nValidating invite...")
    val_resp = requests.get(f"{BASE_URL}/auth/invite/{invite_token}")
    if val_resp.status_code != 200:
        print("Invite validation failed:", val_resp.text)
        return
    print("Invite is valid!", val_resp.json())

    # 4. Register using Invite
    print("\nRegistering new user with invite...")
    reg_data = {
        "nome": "Novo Lider",
        "email": f"lider_{int(time.time())}@teste.com",
        "cpf": "12345678901",
        "password": "password123",
        "papel": "lider_de_celula",
        "invite_token": invite_token,
        "cep": "12345678",
        "logradouro": "Rua Teste",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "Cidade",
        "estado": "ST"
    }
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if reg_resp.status_code != 201:
        print("Registration failed:", reg_resp.text)
        return
    print("Registration successful!")

    # 5. Try to use same token again
    print("\nTrying to use same token again...")
    reg_data["email"] = f"lider_again_{int(time.time())}@teste.com"
    reg_resp_again = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if reg_resp_again.status_code == 400:
        print("Successfully blocked duplicate use of token!")
    else:
        print("Error: duplicate use of token was NOT blocked!", reg_resp_again.text)

if __name__ == "__main__":
    test_invite_flow()
