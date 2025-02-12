from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from collections import defaultdict
import time
from typing import List, Optional
from auth_utils import (
    Token, UserInDB, authenticate_user, create_access_token, get_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
)
from jose import JWTError, jwt

app = FastAPI(title="API Gateway")

# Pydantic models for request/response validation
class User(BaseModel):
    id: int = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's name")
    email: str | None = Field(None, description="User's email")
    
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error description")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.now)

class RateLimitInfo(BaseModel):
    limit: int = Field(..., description="Maximum requests allowed")
    remaining: int = Field(..., description="Remaining requests in window")
    window_seconds: int = Field(..., description="Time window in seconds")

# Configuration
BACKEND_SERVICE_URL = "http://localhost:8001"
HTTP_TIMEOUT = 30.0
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, client_id: str) -> tuple[bool, RateLimitInfo]:
        now = time.time()
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if client exceeded rate limit
        requests_remaining = max(0, self.requests_limit - len(self.requests[client_id]))
        is_limited = len(self.requests[client_id]) >= self.requests_limit
        
        # Add new request timestamp if not limited
        if not is_limited:
            self.requests[client_id].append(now)
        
        return is_limited, RateLimitInfo(
            limit=self.requests_limit,
            remaining=requests_remaining,
            window_seconds=self.window_seconds
        )

# Initialize rate limiter
rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

# Create a reusable HTTP client
http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_client_id(request: Request) -> str:
    return request.client.host

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Gateway health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="gateway"
    )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint to get JWT token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users", response_model=List[User])
async def get_users(
    request: Request,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get users endpoint with rate limiting and authentication
    """
    client_id = get_client_id(request)
    is_limited, rate_limit_info = rate_limiter.is_rate_limited(client_id)
    
    headers = {
        "X-RateLimit-Limit": str(rate_limit_info.limit),
        "X-RateLimit-Remaining": str(rate_limit_info.remaining),
        "X-RateLimit-Window": f"{rate_limit_info.window_seconds}s"
    }
    
    if is_limited:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers=headers
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_SERVICE_URL}/users")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Backend service error: {str(exc)}"
        )

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
