"""Authentication API router."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services.auth import create_access_token, verify_credentials, verify_token


router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT token."""
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    access_token = create_access_token(request.username)
    return TokenResponse(access_token=access_token)


@router.get("/verify")
async def verify(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token is valid."""
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    return {"valid": True, "username": username}
