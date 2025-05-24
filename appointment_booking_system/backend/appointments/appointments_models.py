from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Based on the database_schema.md
class AppointmentBase(BaseModel):
    user_id: str # Link to User.id (from auth_models.UserResponse)
    provider_id: str # Link to a Provider ID (assume providers exist)
    start_time: datetime
    end_time: datetime
    service_description: Optional[str] = None
    notes_user: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass # No extra fields for creation for now

class AppointmentResponse(AppointmentBase):
    appointment_id: str
    status: str = Field(default="scheduled") # Default status
    notes_provider: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
