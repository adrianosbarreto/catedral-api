"""
Script para testar o endpoint de login através do servidor
"""
import requests
import json

def test_api_login():
    url = "http://localhost:5000/catedral/auth/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Enviando requisição POST para {url}...")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ LOGIN BEM SUCEDIDO!")
            print("📦 Resposta JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ FALHA NO LOGIN: {response.status_code}")
            print(f"💬 Resposta: {response.text}")
            
    except Exception as e:
        print(f"💥 ERRO NA REQUISIÇÃO: {e}")

if __name__ == "__main__":
    test_api_login()
