from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional # Added for type hinting if needed, though not strictly for current code

from . import auth_models # Assuming auth_models.py is in the same directory
from . import auth_utils  # Assuming auth_utils.py is in the same directory

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# In-memory user counter for User ID (very basic)
user_id_counter = 0

@router.post("/signup", response_model=auth_models.UserResponse)
async def signup(user: auth_models.UserCreate):
    global user_id_counter
    if user.email in auth_utils.fake_users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = auth_utils.get_password_hash(user.password)
    user_id_counter += 1
    user_id = str(user_id_counter) # Simple incrementing ID

    auth_utils.fake_users_db[user.email] = {
        "id": user_id, # Storing the ID
        "hashed_password": hashed_password,
        "name": user.name,
        "phone_number": user.phone_number,
        "email": user.email # Storing email again for easier retrieval in /users/me
    }
    # Return the created user data (without password)
    return auth_models.UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        phone_number=user.phone_number
    )

@router.post("/login", response_model=auth_models.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_in_db = auth_utils.fake_users_db.get(form_data.username) # form_data.username is the email
    if not user_in_db or not auth_utils.verify_password(form_data.password, user_in_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=auth_models.UserResponse)
async def read_users_me(current_user_payload: dict = Depends(auth_utils.get_current_user)):
    # current_user_payload is the dict {"email": email, "name": name} from get_current_user
    # Fetch the full user details from fake_users_db using the email from the token
    user_details = auth_utils.fake_users_db.get(current_user_payload["email"])
    
    if not user_details:
        # This case should ideally be caught by get_current_user if email not in fake_users_db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Construct UserResponse from the stored user_details
    return auth_models.UserResponse(
        id=user_details["id"],
        email=user_details["email"],
        name=user_details["name"],
        phone_number=user_details["phone_number"]
    )
