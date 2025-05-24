from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: str # For now, can be email or a simple counter
    email: EmailStr
    name: str
    phone_number: Optional[str] = None

    class Config:
        orm_mode = True # Will be useful with ORMs later

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
