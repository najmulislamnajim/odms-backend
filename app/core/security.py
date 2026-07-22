import jwt, hashlib, secrets
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone 

from app.core.config import settings 

# Initialize the hashing helper
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a plain text password securely."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(da_code: str) -> str:
    """Create a signed JWT access token for an authenticated DA."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": da_code,
        "iat": now, 
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> str | None: 
    """Decode and verify a JWT token. Returns da_code if valid, else None."""
    try: 
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None # token expired 
    except jwt.InvalidTokenError:
        return None # invalid / tempered token 
    
def generate_refresh_token() -> str:
    """Generate a cryptographically secure random refresh token."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using SHA-256 for secure storage and fast lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
