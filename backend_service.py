from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

backend = FastAPI(title="Backend Service")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status of the service")
    service: str = Field(..., description="Name of the service")

class User(BaseModel):
    id: int = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's name")
    email: str | None = Field(None, description="User's email")

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
