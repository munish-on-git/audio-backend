from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm

from .security import verify_password, create_access_token, decode_access_token, get_password_hash

# Create a router. This is like a mini-FastAPI app that can be included in the main one.
router = APIRouter()

# User Database and Models (Can be moved to a database module later)
class User:
    def __init__(self, username: str, full_name: str = "Test User"):
        self.username = username; self.full_name = full_name

# For now, we generate 100 test users in memory
fake_users_db = {
    f"user{i}": {
        "username": f"user{i}", 
        "hashed_password": get_password_hash(f"password{i}")
    } 
    for i in range(100)
}

def get_user(username: str):
    if username in fake_users_db:
        return User(username=username)
    return None

def authenticate_user(username: str, password: str):
    if username not in fake_users_db: return False
    user_dict = fake_users_db[username]
    if not verify_password(password, user_dict["hashed_password"]): return False
    return get_user(username)


# Authentication Endpoint 
@router.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Authentication Dependency
async def get_current_user(token: str = Query(...)):
    """A dependency to authenticate users for protected endpoints (like WebSockets)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user