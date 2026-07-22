from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Request body for DA login."""
    da_code: str
    password: str
    force: bool = False


class LoginResponse(BaseModel):
    """Response returned after successful login."""
    access_token: str
    refresh_token: str 
    token_type: str = "bearer"
    must_reset: bool
    
class ChangePasswordRequest(BaseModel):
    """Request body for changing password."""
    old_password: str
    new_password: str
    
class RefreshRequest(BaseModel):
    """Request body for refreshing an access token."""
    refresh_token: str


class RefreshResponse(BaseModel):
    """Response with a new access token."""
    access_token: str
    token_type: str = "bearer"