"""
Authentication Module for Smart Agriculture API
"""
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic Security
security = HTTPBasic()

# In-memory user database (replace with real database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "email": "admin@smartagriculture.com"
    },
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user",
        "email": "user@smartagriculture.com"
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> Optional[dict]:
    """Get user from database"""
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user['hashed_password']):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
        
        user = get_user(username)
        return user
        
    except JWTError:
        return None


async def get_current_user(credentials: HTTPBasicCredentials = Security(security)) -> dict:
    """Get current authenticated user (HTTP Basic Auth)"""
    try:
        user = authenticate_user(credentials.username, credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        
        logger.info(f"User authenticated: {user['username']}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Basic"},
        )


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user"""
    if current_user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """Role-based access control"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: dict = Depends(get_current_active_user)) -> dict:
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user


# Role checkers
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["admin", "user"])


def generate_api_key() -> str:
    """Generate API key"""
    return secrets.token_urlsafe(32)


# API Key validation (simple in-memory store)
API_KEYS = {
    "admin-api-key": {"username": "admin", "role": "admin"},
    "user-api-key": {"username": "user", "role": "user"}
}


async def verify_api_key(api_key: str) -> Optional[dict]:
    """Verify API key"""
    return API_KEYS.get(api_key)


if __name__ == "__main__":
    # Test authentication
    print("Testing Authentication...")
    print("="*80)
    
    # Test password verification
    print("\n1. Testing password verification:")
    test_password = "admin123"
    user = USERS_DB["admin"]
    
    is_valid = verify_password(test_password, user['hashed_password'])
    print(f"  Password valid: {is_valid}")
    
    # Test authentication
    print("\n2. Testing user authentication:")
    authenticated = authenticate_user("admin", "admin123")
    if authenticated:
        print(f"  Authenticated: {authenticated['username']} ({authenticated['role']})")
    else:
        print("  Authentication failed")
    
    # Test token creation
    print("\n3. Testing JWT token creation:")
    token = create_access_token(data={"sub": "admin"})
    print(f"  Token created: {token[:50]}...")
    
    # Test token verification
    print("\n4. Testing JWT token verification:")
    user = verify_token(token)
    if user:
        print(f"  Token valid for: {user['username']}")
    else:
        print("  Token invalid")
    
    # Test API key generation
    print("\n5. Testing API key generation:")
    api_key = generate_api_key()
    print(f"  Generated API key: {api_key}")
    
    print("\n✓ Authentication test complete!")