from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time

class AvailabilityQuery(BaseModel):
    target_date: date
    service_type: Optional[str] = None # For AI to suggest duration
    user_id: Optional[str] = None # For AI to fetch user preferences

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime

class ProviderAvailabilityResponse(BaseModel):
    provider_id: str
    date: date
    available_slots: List[TimeSlot]
    # Could add suggestion metadata here from AI service later
