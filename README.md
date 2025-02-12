# API Gateway with Rate Limiting and Authentication

A FastAPI-based API Gateway implementation featuring rate limiting, JWT authentication, file upload, and request proxying to backend services.

## Features

- 🔒 JWT Authentication
- ⏱️ Rate Limiting (10 requests per minute per client)
- 🔄 Request Proxying
- 🛡️ Protected Endpoints
- 📤 File Upload Support
- 🧪 Comprehensive Testing Suite


## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone the repository
2. Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

Key configurations are defined in the respective files:

### Authentication (`auth_utils.py`)
- `SECRET_KEY`: JWT secret key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)
- Test user credentials:
  - Username: testuser
  - Password: testpassword

### Rate Limiting (`gateway.py`)
- `RATE_LIMIT_REQUESTS`: Maximum requests per window (default: 10)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)

### Services (`gateway.py`)
- Gateway Service: http://localhost:8000
- Backend Service: http://localhost:8001

## Running the Services

Start both the gateway and backend services:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /token`
  - Get JWT access token
  - Body: `username` and `password` (form-data)

### Protected Endpoints
- `GET /api/users`
  - Requires JWT authentication
  - Rate limited (10 requests/minute)
  - Returns list of users

- `POST /api/upload-zip`
  - Requires JWT authentication
  - Upload ZIP files
  - Returns upload details including filename, size, and timestamp

### Health Check
- `GET /health`
  - Service health status
  - No authentication required

## Testing

### Rate Limit Testing
```bash
python test_rate_limit.py
```
This will test:
1. Unauthorized access
2. Invalid token access
3. Rate limiting with valid authentication

### File Upload Testing
```bash
python test_upload.py
```
Test file upload functionality with:
1. Authentication check
2. ZIP file validation
3. Upload success verification

## Response Headers

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Window`: Time window in seconds

## Error Responses

- 401: Unauthorized (missing or invalid token)
- 429: Too Many Requests (rate limit exceeded)
- 503: Backend Service Unavailable

## Security Considerations

For production deployment:
1. Use environment variables for sensitive data
2. Enable HTTPS
3. Implement proper user management
4. Use secure password hashing
5. Implement refresh tokens
6. Regular security audits

## Development

To modify rate limits or add new features:
1. Update configuration in respective files
2. Add new endpoints in `gateway.py`
3. Update tests accordingly
4. Run test suite to verify changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## File Upload Configuration

The backend service stores uploaded files in:
- Upload directory: `uploads/` (created automatically)
- Files are renamed with timestamp prefix for uniqueness
- Only ZIP files are accepted
- Upload response includes:
  - Filename
  - File size
  - Upload timestamp
  - Upload status

## API Documentation

### Swagger UI
The API documentation is available via Swagger UI at `http://localhost:8000/docs`. The interactive documentation includes:

#### Endpoint Groups
- 🔒 **Authentication**
  - POST `/token` - Get JWT access token
- 👥 **Users**
  - GET `/api/users` - Get list of users
- 📤 **File Upload**
  - POST `/api/upload-zip` - Upload ZIP files
- 🏥 **Health**
  - GET `/health` - Service health check

#### Features
- Interactive API testing interface
- Request/response schema documentation
- Authentication flow demonstration
- Sample request bodies
- Response code descriptions
- Rate limit information

To use Swagger UI:
1. Start the server: `python run.py`
2. Visit `http://localhost:8000/docs` in your browser
3. Authenticate using the `/token` endpoint
4. Test other endpoints with the received JWT token

