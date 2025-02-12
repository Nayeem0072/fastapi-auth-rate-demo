import requests
import os

def get_token(username: str = "testuser", password: str = "testpassword") -> str:
    """Get authentication token"""
    response = requests.post(
        "http://localhost:8000/token",
        data={"username": username, "password": password}
    )
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.json()['detail']}")
    return response.json()["access_token"]

def test_zip_path(file_path: str):
    """Test ZIP file upload"""
    # Get authentication token
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return
    
    # Check if file is a ZIP
    if not file_path.endswith('.zip'):
        print("Error: File must be a ZIP file")
        return
    
    print(f"\nUploading file: {file_path}")
    print("=" * 50)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/zip')}
            response = requests.post(
                "http://localhost:8000/api/upload-zip",
                headers=headers,
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("\nUpload Successful:")
            print(f"Filename: {result['filename']}")
            print(f"Size: {result['size']} bytes")
            print(f"Upload Time: {result['upload_time']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {response.json()['detail']}")
            
    except Exception as e:
        print(f"Error during upload: {str(e)}")

if __name__ == "__main__":
    # Replace with path to your test ZIP file
    zip_file_path = "test.zip"
    test_zip_path(zip_file_path) 