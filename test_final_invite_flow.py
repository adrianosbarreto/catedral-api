
import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_final_invite_flow():
    # 1. Login
    print("Testing login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate Invite
    print("\nGenerating invite...")
    gen_resp = requests.post(f"{BASE_URL}/auth/invite", json={"ide_id": 1}, headers=headers)
    invite_data = gen_resp.json()
    invite_token = invite_data["token"]
    print(f"Invite generated: {invite_token}")

    # 3. Verify Expiration Logic (Internal Check)
    # We can't wait until tomorrow, but we can verify the 'data_expiracao' in the validation response
    print("\nVerifying expiration metadata...")
    val_resp = requests.get(f"{BASE_URL}/auth/invite/{invite_token}")
    val_data = val_resp.json()
    exp_date = val_data["data_expiracao"]
    print(f"Invite expires at: {exp_date}")
    # Should be tomorrow at 23:59:59
    
    # 4. Multi-use Registration
    print("\nRegistering User A...")
    user_a_data = {
        "nome": "User A",
        "email": f"usera_{int(time.time())}@test.com",
        "cpf": "11122233344",
        "password": "password123", # Registrant sets THEIR password
        "papel": "lider_de_celula",
        "invite_token": invite_token
    }
    resp_a = requests.post(f"{BASE_URL}/auth/register", json=user_a_data)
    print("User A registration status:", resp_a.status_code)
    assert resp_a.status_code == 201

    print("\nRegistering User B (Same Token)...")
    user_b_data = {
        "nome": "User B",
        "email": f"userb_{int(time.time())}@test.com",
        "cpf": "55566677788",
        "password": "password456",
        "papel": "vice_lider_de_celula",
        "invite_token": invite_token
    }
    resp_b = requests.post(f"{BASE_URL}/auth/register", json=user_b_data)
    print("User B registration status:", resp_b.status_code)
    assert resp_b.status_code == 201
    print("SUCCESS: Multi-use flow verified!")

    # 5. Verify login for User A
    print("\nVerifying login for User A...")
    login_a = requests.post(f"{BASE_URL}/auth/login", json={
        "username": user_a_data["email"],
        "password": user_a_data["password"]
    })
    print("User A login status:", login_a.status_code)
    assert login_a.status_code == 200
    print("SUCCESS: User A can login with their chosen password!")

if __name__ == "__main__":
    test_final_invite_flow()
