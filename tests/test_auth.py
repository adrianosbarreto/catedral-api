
def test_home_page(client):
    """Test that the home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Igreja em Foco API' in response.data

def test_auth_me_unauthorized(client):
    """Test /auth/me returns 401 for unauthenticated user."""
    response = client.get('/auth/me')
    assert response.status_code == 401
