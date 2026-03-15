
import requests

def test_endpoint(url):
    try:
        response = requests.get(url)
        print(f"Testing {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error testing {url}: {e}")

# Assuming server is on http://localhost:5000 (standard Flask port) or 5173 (Vite proxy?)
# Looking at server.py might tell us the port.
test_endpoint("http://localhost:5000/catedral/api/celulas/public/nearby?lat=-1.4716302&lng=-48.4910653&radius=10")
test_endpoint("http://localhost:5000/catedral/api/celulas/nearby?lat=-1.4716302&lng=-48.4910653&radius=10")
