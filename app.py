# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi.responses import HTMLResponse
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from typing import Optional

# # Constants
# SECRET_KEY = "supersecretkeydontshare"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # FastAPI app
# app = FastAPI() 

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Dummy user database
# # Dummy user database with 5 users
# fake_users_db = {
#     "akash": {
#         "username": "akash",
#         "full_name": "Akash Dutta",
#         "email": "akash@example.com",
#         "hashed_password": pwd_context.hash("password123"),
#         "disabled": False,
#     },
#     "john": {
#         "username": "john",
#         "full_name": "John Smith",
#         "email": "john@example.com",
#         "hashed_password": pwd_context.hash("pass456"),
#         "disabled": False,
#     },
#     "emma": {
#         "username": "emma",
#         "full_name": "Emma Johnson",
#         "email": "emma@example.com",
#         "hashed_password": pwd_context.hash("secret789"),
#         "disabled": False,
#     },
#     "dave": {
#         "username": "dave",
#         "full_name": "Dave Lee",
#         "email": "dave@example.com",
#         "hashed_password": pwd_context.hash("davepass"),
#         "disabled": False,
#     },
#     "sara": {
#         "username": "sara",
#         "full_name": "Sara Parker",
#         "email": "sara@example.com",
#         "hashed_password": pwd_context.hash("sarapass"),
#         "disabled": False,
#     }
# }

# # User model
# class User:
#     def __init__(self, username, full_name, email, disabled):
#         self.username = username
#         self.full_name = full_name
#         self.email = email
#         self.disabled = disabled

# class UserInDB(User):
#     def __init__(self, username, full_name, email, hashed_password, disabled):
#         super().__init__(username, full_name, email, disabled)
#         self.hashed_password = hashed_password

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)

# def authenticate_user(username: str, password: str):
#     user = get_user(fake_users_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username)
#     if user is None:
#         raise credentials_exception
#     return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# # Routes
# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @app.get("/", response_class=HTMLResponse)
# async def home():
#     return "<h2>FastAPI Secure OAuth2 Backend Running</h2>"

# @app.get("/users/me") 
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return {
#         "username": current_user.username,
#         "full_name": current_user.full_name,
#         "email": current_user.email,
#     }

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# === Constants ===
SECRET_KEY = "supersecretkeydontshare"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# === FastAPI app ===
app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:8501",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# === Dummy Users ===
fake_users_db = {
    "akash": {
        "username": "akash",
        "full_name": "Akash Dutta",
        "email": "akash@example.com",
        "hashed_password": pwd_context.hash("password123"),
        "disabled": False,
    },
    "john": {
        "username": "john",
        "full_name": "John Smith",
        "email": "john@example.com",
        "hashed_password": pwd_context.hash("pass456"),
        "disabled": False,
    },
    "emma": {
        "username": "emma",
        "full_name": "Emma Johnson",
        "email": "emma@example.com",
        "hashed_password": pwd_context.hash("secret789"),
        "disabled": False,
    },
    "dave": {
        "username": "dave",
        "full_name": "Dave Lee",
        "email": "dave@example.com",
        "hashed_password": pwd_context.hash("davepass"),
        "disabled": False,
    },
    "sara": {
        "username": "sara",
        "full_name": "Sara Parker",
        "email": "sara@example.com",
        "hashed_password": pwd_context.hash("sarapass"),
        "disabled": False,
    }
}

# === User Models ===
class User:
    def __init__(self, username, full_name, email, disabled):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.disabled = disabled

class UserInDB(User):
    def __init__(self, username, full_name, email, hashed_password, disabled):
        super().__init__(username, full_name, email, disabled)
        self.hashed_password = hashed_password

# === Auth Helpers ===
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === Dependency ===
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h2>FastAPI Secure OAuth2 Backend Running (No SSL)</h2>"

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }
