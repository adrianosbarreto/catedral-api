import requests
import json
import secrets

BASE_URL = 'http://localhost:5000' # Adjust if needed

def test_registration_with_sex():
    # 1. Get an invite token (requires login as admin/pastor/supervisor)
    # For this test, let's assume we can create an invite or use an existing one if we had its IDE_ID
    # But since /register is public if it has a token, we need a valid token.
    # Alternatively, we can mock the token validation if we were running inside the app context.
    
    # Let's try to register directly if ide_id is allowed (it might not be without token based on logic)
    # The logic says: if not ide_id: error. ide_id can come from data if no token.
    
    email = f"test_{secrets.token_hex(4)}@example.com"
    data = {
        "nome": "Test User",
        "email": email,
        "cpf": "12345678901",
        "password": "password123",
        "papel": "lider_de_celula",
        "sexo": "Masculino",
        "ide_id": 1, # Hardcoded for test, adjust to a valid IDE ID in your DB
        "logradouro": "Rua Teste",
        "numero": "123",
        "bairro": "Bairro Teste",
        "cidade": "Cidade Teste",
        "estado": "TS",
        "cep": "12345-678"
    }
    
    print(f"Testing registration for {email} with sexo: {data['sexo']}")
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        print(response.json())
        
        # Verify if saved correctly (would need login to check members API)
        # But for now, 201 is a good sign that the backend accepted the field.
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_registration_with_sex()
