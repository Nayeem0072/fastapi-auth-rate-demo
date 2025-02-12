import requests
from typing import Optional

def get_token(username: str, password: str) -> Optional[str]:
    """Get authentication token"""
    response = requests.post(
        "http://localhost:8000/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Authentication failed: {response.status_code}")
    try:
        print(response.json())
    except:
        print(response.text)
    return None

def test_protected_endpoint(token: str):
    """Test accessing protected endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with authentication
    response = requests.get(
        "http://localhost:8000/api/users",
        headers=headers
    )
    print("\nWith valid token:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response text: {response.text}")
    
    # Test without authentication
    response = requests.get("http://localhost:8000/api/users")
    print("\nWithout token:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response text: {response.text}")

if __name__ == "__main__":
    # Get token
    token = get_token("testuser", "testpassword")
    if token:
        test_protected_endpoint(token) 