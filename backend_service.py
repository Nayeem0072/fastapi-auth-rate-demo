from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field
from typing import List
import os
from datetime import datetime
import aiofiles
from fastapi import HTTPException

backend = FastAPI(title="Backend Service")

# Add configuration for upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status of the service")
    service: str = Field(..., description="Name of the service")

class User(BaseModel):
    id: int = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's name")
    email: str | None = Field(None, description="User's email")

class UploadResponse(BaseModel):
    filename: str
    size: int
    upload_time: datetime
    status: str

@backend.get("/health", response_model=HealthResponse)
async def backend_health():
    """Backend service health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="backend"
    )

@backend.get("/users", response_model=List[User])
async def get_users():
    """Sample backend endpoint with response validation"""
    return [
        User(id=1, name="Alice", email="alice@example.com"),
        User(id=2, name="Bob", email="bob@example.com"),
        User(id=3, name="Charlie", email=None)
    ]

@backend.post("/upload-zip", response_model=UploadResponse)
async def upload_zip_file(file: UploadFile = File(...)):
    """Handle ZIP file upload"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed"
        )
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return UploadResponse(
            filename=filename,
            size=file_size,
            upload_time=datetime.now(),
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
