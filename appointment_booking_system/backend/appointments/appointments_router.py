from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from datetime import datetime, timezone # Added timezone
import uuid # For generating appointment_id

from . import appointments_models
# Assuming 'backend' is in PYTHONPATH or the execution context handles it.
try:
    from backend.auth.auth_utils import get_current_user
except ImportError:
    # Fallback for direct execution or certain testing setups
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(SCRIPT_DIR) # This should be 'backend'
    GRANDPARENT_DIR = os.path.dirname(PARENT_DIR) # This should be 'appointment_booking_system'
    if GRANDPARENT_DIR not in sys.path:
        sys.path.insert(0, GRANDPARENT_DIR)
    from backend.auth.auth_utils import get_current_user


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
    # Add dependency for authentication to all routes in this router if needed
    # dependencies=[Depends(get_current_user)] 
    # For now, let's add it per-route to be explicit
)

# In-memory storage for appointments
fake_appointments_db: List[appointments_models.AppointmentResponse] = []

@router.post("/", response_model=appointments_models.AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: appointments_models.AppointmentCreate, 
    current_user: dict = Depends(get_current_user) # Ensure user is authenticated
):
    # Basic validation (in a real app, check provider exists, slot is available via scheduler_service)
    if appointment.end_time <= appointment.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time must be after start time.")
    
    # Ensure times are timezone-aware if needed, or handle conversion. Pydantic v2 might handle this better.
    # For now, assuming naive datetimes or that they are handled consistently.

    # TODO: Integrate with scheduler_service to verify availability
    # TODO: Integrate with ai_service for suggestions if not fully specified

    new_appointment_id = str(uuid.uuid4())
    
    # Get current user's ID. Assuming get_current_user returns a dict that includes user's ID.
    # The auth_router.py for /users/me returns a UserResponse model which has an 'id' field.
    # However, get_current_user in auth_utils.py returns a dict: {"email": email, "name": name}
    # We need to ensure current_user['id'] is available or adjust.
    # For now, using email as user_id as per previous implementations.
    # A better approach would be to have get_current_user return a UserResponse model or a consistent user object.
    user_id_for_appointment = current_user["email"] 
    # If auth_utils.fake_users_db stores the user ID, get_current_user should fetch and return it.
    # Let's assume for now `current_user["email"]` is the intended link for `user_id`.

    db_appointment = appointments_models.AppointmentResponse(
        appointment_id=new_appointment_id,
        user_id=user_id_for_appointment, 
        provider_id=appointment.provider_id,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        service_description=appointment.service_description,
        notes_user=appointment.notes_user,
        status="scheduled", # Default status
        created_at=datetime.now(timezone.utc), # Use timezone aware datetime
        updated_at=datetime.now(timezone.utc), # Use timezone aware datetime
    )
    fake_appointments_db.append(db_appointment)
    return db_appointment

@router.get("/user/{user_id_param}", response_model=List[appointments_models.AppointmentResponse])
async def get_user_appointments(
    user_id_param: str = Path(..., alias="user_id"), # Use alias to avoid conflict
    current_user: dict = Depends(get_current_user) # Authenticated user
):
    # Authorization: Ensure current_user can only access their own appointments (or if admin)
    # Assuming 'email' is the identifier in current_user dict from get_current_user
    if current_user["email"] != user_id_param and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these appointments")
    
    user_apps = [app for app in fake_appointments_db if app.user_id == user_id_param]
    return user_apps

@router.get("/{appointment_id}", response_model=appointments_models.AppointmentResponse)
async def get_appointment_details(
    appointment_id: str = Path(..., title="The ID of the appointment to get"),
    current_user: dict = Depends(get_current_user) # Authenticated user
):
    appointment = next((app for app in fake_appointments_db if app.appointment_id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    # Authorization: Ensure user can only access their own appointments or if provider/admin
    # Assuming 'email' is the identifier in current_user dict
    if appointment.user_id != current_user["email"] and "admin" not in current_user.get("roles", []): # and provider_id is not theirs
        # TODO: Add check if current_user is the provider_id for this appointment
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this appointment")
    return appointment

@router.put("/{appointment_id}/cancel", response_model=appointments_models.AppointmentResponse)
async def cancel_appointment(
    appointment_id: str = Path(..., title="The ID of the appointment to cancel"),
    current_user: dict = Depends(get_current_user) # Authenticated user
):
    appointment_to_cancel = None
    for i, app in enumerate(fake_appointments_db):
        if app.appointment_id == appointment_id:
            appointment_to_cancel = app
            break
    
    if not appointment_to_cancel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # Authorization: User can cancel their own, provider can cancel theirs (add later)
    # Assuming 'email' is the identifier in current_user dict
    if appointment_to_cancel.user_id != current_user["email"] and "admin" not in current_user.get("roles",[]):
        # TODO: Add check if current_user is the provider_id for this appointment
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this appointment")

    if appointment_to_cancel.status.startswith("cancelled"): # Handles "cancelled_by_user", "cancelled_by_provider"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment already cancelled.")

    appointment_to_cancel.status = "cancelled_by_user" # Or determine if provider is cancelling
    appointment_to_cancel.updated_at = datetime.now(timezone.utc) # Use timezone aware datetime
    
    # Update in the list (since it's a mutable object, changes are reflected)
    # If it were an immutable object, we'd need to replace it: fake_appointments_db[i] = appointment_to_cancel
       
    # TODO: Notify provider/user via notification_service
    return appointment_to_cancel

# Placeholder for provider appointments (can be expanded)
@router.get("/provider/{provider_id}", response_model=List[appointments_models.AppointmentResponse])
async def get_provider_appointments(
    provider_id: str,
    # current_user: dict = Depends(get_current_user) # TODO: Add auth, ensure current_user is this provider or admin
):
    # TODO: Add authorization logic here if current_user is the provider or an admin
    # Example:
    # if current_user.get("provider_id") != provider_id and "admin" not in current_user.get("roles", []):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    provider_apps = [app for app in fake_appointments_db if app.provider_id == provider_id]
    return provider_apps
