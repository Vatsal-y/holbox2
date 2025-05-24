from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# In-memory user store (for now, replace with DB later)
fake_users_db = {} # Store hashed passwords

# Configuration (move to a config file later)
SECRET_KEY = "a_very_secret_key_for_jwt" # Replace with a strong, generated key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Adjusted tokenUrl

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Basic function to get current user (very simplified for now)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # In a real app, you'd fetch user from DB here
        if email not in fake_users_db: # Check if user exists
            raise credentials_exception
        # Return a dummy user object or email for now
        # The UserResponse model expects 'id' as well.
        # We need to ensure fake_users_db stores this or the get_current_user can construct it.
        # For now, let's return a dict that can be expanded by the calling route.
        return {"email": email, "name": fake_users_db[email].get("name", "Unknown")}
    except JWTError:
        raise credentials_exception
