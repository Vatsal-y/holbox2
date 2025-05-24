from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from typing import List
from datetime import date, datetime, timedelta, time # Ensure time is imported

from . import providers_models
# Assuming services are structured to be importable:

# Handle imports with try-except for flexibility in execution context
try:
    from backend.scheduler_service.core import get_available_slots
    from backend.ai_service.suggestions import get_suggested_duration, get_preferred_time_windows
    from backend.auth.auth_utils import get_current_user # For user_id context
except ImportError:
    # This block allows the code to be more resilient if the 'backend' package structure
    # isn't perfectly recognized in all execution environments (e.g. some test runners, direct script exec)
    # It assumes that if 'from backend...' fails, the modules might be findable directly
    # or through sys.path manipulations if those were done by a calling script.
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(SCRIPT_DIR) # This should be 'backend'
    GRANDPARENT_DIR = os.path.dirname(PARENT_DIR) # This should be 'appointment_booking_system'
    if GRANDPARENT_DIR not in sys.path:
        sys.path.insert(0, GRANDPARENT_DIR)
    
    from backend.scheduler_service.core import get_available_slots
    from backend.ai_service.suggestions import get_suggested_duration, get_preferred_time_windows
    from backend.auth.auth_utils import get_current_user


router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
)

# --- SIMULATED DATA (Mimic what scheduler_service/core.py expects) ---
# This should ideally be managed by the scheduler_service or a shared data module
# For now, replicate some structure here for the endpoint to use.
# In a real setup, the scheduler_service would handle its own data sources.

# Data format for scheduler_service.core.get_available_slots:
# provider_availability_data: List of dicts, each dict represents a rule.
# existing_appointments_data: List of dicts, each dict is an appointment.
# time_off_data: List of dicts, each dict is a time-off block.

# For this endpoint, we are looking up a specific provider_id.
# So, the mock data should be structured to allow fetching data for a specific provider.
# The scheduler_service.core.sample_provider_availability_data is a flat list.
# We need to adapt or pre-filter it here for the router.

# Using the exact sample data from scheduler_service.core for consistency
# This data will be filtered by provider_id within the endpoint logic.
mock_scheduler_provider_rules = [
    {
        'provider_id': 'prov1', 'day_of_week': 0, # Monday
        'start_time': '09:00', 'end_time': '17:00', 
        'is_active': True, 'valid_from': None, 'valid_until': None
    },
    {
        'provider_id': 'prov1', 'day_of_week': 2, # Wednesday
        'start_time': '10:00', 'end_time': '16:00',
        'is_active': True, 'valid_from': None, 'valid_until': None
    },
    { # Data for prov_dr_smith as per task description
        'provider_id': 'prov_dr_smith', 'day_of_week': 0, # Monday
        'start_time': '09:00', 'end_time': '12:00', 
        'is_active': True, 'valid_from': None, 'valid_until': None
    },
    {
        'provider_id': 'prov_dr_smith', 'day_of_week': 0, # Monday
        'start_time': '13:00', 'end_time': '17:00', 
        'is_active': True, 'valid_from': None, 'valid_until': None
    },
    { # Another provider for testing
        'provider_id': 'prov2', 'day_of_week': 0, # Monday
        'start_time': '10:00', 'end_time': '18:00',
        'is_active': True, 'valid_from': None, 'valid_until': None
    }
]

mock_scheduler_appointments = [
    {
        'provider_id': 'prov1', 
        'start_time': datetime(2024, 8, 5, 10, 0), # Example for a Monday
        'end_time': datetime(2024, 8, 5, 11, 0)
    },
    { # Adding another appointment for prov1 on a different day for completeness
        'provider_id': 'prov1',
        'start_time': datetime(2024, 8, 7, 14, 0), # Example for a Wednesday
        'end_time': datetime(2024, 8, 7, 14, 30)
    }
    # No appointments for prov_dr_smith or prov2 in this mock for simplicity
]

mock_scheduler_time_offs = [
    {
        'provider_id': 'prov1',
        'start_time': datetime(2024, 8, 5, 12, 0), # Monday
        'end_time': datetime(2024, 8, 5, 13, 0)
    }
    # No time_off for prov_dr_smith or prov2
]
# --- END SIMULATED DATA ---


@router.post("/{provider_id}/availability", response_model=providers_models.ProviderAvailabilityResponse)
async def get_provider_availability(
    provider_id: str = Path(..., title="The ID of the provider"),
    query: providers_models.AvailabilityQuery = Body(...),
    # current_user: dict = Depends(get_current_user) # Optional: if user_id from token is preferred over query
):
    # 1. Determine appointment duration
    user_id_for_ai = query.user_id 
    # If current_user dependency is used and query.user_id is None, you might use:
    # user_id_for_ai = query.user_id or current_user.get("email") # or current_user.get("id")
       
    suggested_duration_minutes = 60 # Default
    if user_id_for_ai:
        # ai_service.suggestions.get_suggested_duration expects user_id and optional service_type
        suggested_duration_minutes = get_suggested_duration(user_id_for_ai, query.service_type)
    elif query.service_type: # Basic fallback if no user, but service type known
        if query.service_type == "quick_checkup": suggested_duration_minutes = 15
        elif query.service_type == "standard_consultation": suggested_duration_minutes = 45
        # Add more service type to duration mappings as needed
    
    # 2. Fetch provider's schedule data (using mocks, filtered for the provider_id)
    # The scheduler_service.core.get_available_slots expects data for ALL providers
    # and then filters internally by provider_id. So, we pass the full mock lists.

    # Check if the provider_id exists in any of the availability rules.
    # This is a simple check to see if we "know" this provider.
    if not any(rule['provider_id'] == provider_id for rule in mock_scheduler_provider_rules):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider {provider_id} not found or has no schedule rules defined.")

    # 3. Call the scheduler_service logic
    # Ensure that the time format in mock_scheduler_provider_rules ('HH:MM') is correctly handled
    # by get_available_slots, which expects time strings or time objects.
    # The original scheduler_service.core.py used 'HH:MM' strings and converted them.
    available_raw_slots = get_available_slots(
        provider_id=provider_id,
        target_date=query.target_date,
        provider_availability_data=mock_scheduler_provider_rules, 
        existing_appointments_data=mock_scheduler_appointments, 
        time_off_data=mock_scheduler_time_offs, 
        slot_duration_minutes=suggested_duration_minutes
    )

    # 4. Format slots for response
    # The get_available_slots returns list of (datetime, datetime) tuples
    formatted_slots = [providers_models.TimeSlot(start_time=slot[0], end_time=slot[1]) for slot in available_raw_slots]

    # (Optional step for later: Filter slots based on get_preferred_time_windows from ai_service)
    # if user_id_for_ai:
    #     preferred_windows = get_preferred_time_windows(user_id_for_ai, query.target_date)
    #     # Filter formatted_slots based on these preferred_windows (complex logic, for future)
    #     # This would involve converting preferred_windows (which are string times like "09:00")
    #     # to datetime.time objects and then checking if each formatted_slot falls within such a window.

    return providers_models.ProviderAvailabilityResponse(
        provider_id=provider_id,
        date=query.target_date,
        available_slots=formatted_slots
    )
