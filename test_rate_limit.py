import requests
import time
from datetime import datetime

def get_token(username: str = "testuser", password: str = "testpassword") -> str:
    """Get authentication token"""
    response = requests.post(
        "http://localhost:8000/token",
        data={"username": username, "password": password}
    )
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.json()['detail']}")
    return response.json()["access_token"]

def test_rate_limit():
    # First get the authentication token
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    url = "http://localhost:8000/api/users"
    
    print("\nTesting rate limiting (12 requests) with authentication...")
    print("=" * 50)
    
    for i in range(12):
        response = requests.get(url, headers=headers)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Extract rate limit headers
        limit = response.headers.get('X-RateLimit-Limit', 'N/A')
        remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
        window = response.headers.get('X-RateLimit-Window', 'N/A')
        
        print(f"\nRequest {i+1} at {timestamp}")
        print(f"Status Code: {response.status_code}")
        print(f"Rate Limit: {limit}")
        print(f"Remaining: {remaining}")
        print(f"Window: {window}")
        
        if response.status_code != 200:
            try:
                error_detail = response.json()['detail']
                print(f"Error Message: {error_detail}")
            except:
                print(f"Error Message: {response.text}")

def test_rate_limit_without_auth():
    """Test rate limiting without authentication"""
    url = "http://localhost:8000/api/users"
    
    print("\nTesting endpoint without authentication...")
    print("=" * 50)
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Error Message: {response.json()['detail']}")
    except:
        print(f"Response: {response.text}")

def test_rate_limit_with_invalid_token():
    """Test rate limiting with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    url = "http://localhost:8000/api/users"
    
    print("\nTesting endpoint with invalid token...")
    print("=" * 50)
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Error Message: {response.json()['detail']}")
    except:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Starting Rate Limit Tests")
    print("=" * 50)
    
    # Test 1: Without authentication
    test_rate_limit_without_auth()
    
    # Test 2: With invalid token
    test_rate_limit_with_invalid_token()
    
    # Test 3: With valid authentication and rate limiting
    test_rate_limit() 