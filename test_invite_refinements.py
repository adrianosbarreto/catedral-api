
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_invite_refinements():
    # 1. Login as Admin
    print("Testing login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login success!")

    # 2. Generate Invite with Password
    print("\nGenerating invite with password...")
    invite_pwd = "SecretPassword"
    gen_resp = requests.post(f"{BASE_URL}/auth/invite", json={
        "ide_id": 1,
        "senha": invite_pwd
    }, headers=headers)
    
    invite_data = gen_resp.json()
    invite_token = invite_data["token"]
    print(f"Invite generated! Token: {invite_token}")

    # 3. Validate Invite (should say password is required)
    print("\nValidating invite...")
    val_resp = requests.get(f"{BASE_URL}/auth/invite/{invite_token}")
    val_data = val_resp.json()
    print("Invite validation response:", val_data)
    assert val_data["requer_senha"] == True

    # 4. Register with WRONG invite password
    print("\nRegistering with WRONG password...")
    reg_data = {
        "nome": "Erro Lider",
        "email": f"erro_{int(time.time())}@test.com",
        "cpf": "12345678901",
        "password": "pwd",
        "papel": "lider_de_celula",
        "invite_token": invite_token,
        "senha_convite": "WrongPassword"
    }
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    print("Registration response (expected 401):", reg_resp.status_code, reg_resp.text)
    assert reg_resp.status_code == 401

    # 5. Register with CORRECT invite password
    print("\nRegistering with CORRECT password (User 1)...")
    reg_data["email"] = f"user1_{int(time.time())}@test.com"
    reg_data["senha_convite"] = invite_pwd
    reg_resp1 = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    print("Registration 1 response:", reg_resp1.status_code)
    assert reg_resp1.status_code == 201

    # 6. Multi-use: Register AGAIN with same token
    print("\nRegistering User 2 with SAME token (Multi-use test)...")
    reg_data["email"] = f"user2_{int(time.time())}@test.com"
    reg_resp2 = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    print("Registration 2 response:", reg_resp2.status_code)
    assert reg_resp2.status_code == 201
    print("SUCCESS: Multi-use verification passed!")

if __name__ == "__main__":
    test_invite_refinements()
