# core.py - Module for smart scheduling logic

from datetime import datetime, date, time, timedelta

# --- Step 2: Define Data Structures (Simulating DB Data) ---
sample_provider_availability_data = [
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
    {
        'provider_id': 'prov2', 'day_of_week': 0, # Monday
        'start_time': '10:00', 'end_time': '18:00',
        'is_active': True, 'valid_from': None, 'valid_until': None
    }
]

sample_existing_appointments_data = [
    {
        'provider_id': 'prov1', 
        'start_time': datetime(2024, 7, 29, 10, 0), # July 29, 2024 is a Monday
        'end_time': datetime(2024, 7, 29, 11, 0)
    },
    {
        'provider_id': 'prov1',
        'start_time': datetime(2024, 7, 29, 14, 0),
        'end_time': datetime(2024, 7, 29, 14, 30)
    }
]

sample_time_off_data = [
    {
        'provider_id': 'prov1',
        'start_time': datetime(2024, 7, 29, 12, 0), # Monday
        'end_time': datetime(2024, 7, 29, 13, 0)
    },
    {
        'provider_id': 'prov1',
        'start_time': datetime(2024, 7, 31, 10, 0), # Wednesday
        'end_time': datetime(2024, 7, 31, 12, 0) # Time off in the morning
    }
]

# --- Step 4: Helper for Time Interval Arithmetic (Simplified) ---
# For this version, we'll use a simpler approach by discretizing time and checking
# rather than full interval arithmetic. A more robust solution would involve
# functions for interval union, intersection, and difference.

def is_slot_available(slot_start: datetime, slot_end: datetime,
                      existing_appointments: list[tuple[datetime, datetime]],
                      time_offs: list[tuple[datetime, datetime]]) -> bool:
    """
    Checks if a single potential slot conflicts with existing appointments or time offs.
    """
    # Check for overlap with existing appointments
    for app_start, app_end in existing_appointments:
        if max(slot_start, app_start) < min(slot_end, app_end):
            return False # Overlap

    # Check for overlap with time offs
    for off_start, off_end in time_offs:
        if max(slot_start, off_start) < min(slot_end, off_end):
            return False # Overlap
            
    return True

# --- Step 3: Implement Slot Generation Logic ---
def get_available_slots(provider_id: str, target_date: date,
                        provider_availability_data: list[dict],
                        existing_appointments_data: list[dict],
                        time_off_data: list[dict],
                        slot_duration_minutes: int = 60) -> list[tuple[datetime, datetime]]:
    """
    Generates available appointment slots for a given provider on a target date.
    """
    available_slots = []
    target_day_of_week = target_date.weekday() # Monday is 0, Sunday is 6

    # a. Determine Base Availability
    base_availability_rules = [
        rule for rule in provider_availability_data
        if rule['provider_id'] == provider_id and \
           rule['day_of_week'] == target_day_of_week and \
           rule['is_active'] and \
           (rule['valid_from'] is None or date.fromisoformat(rule['valid_from']) <= target_date) and \
           (rule['valid_until'] is None or date.fromisoformat(rule['valid_until']) >= target_date)
    ]

    if not base_availability_rules:
        return [] # No general availability for this day

    # For simplicity, assuming one active rule per day for a provider.
    # A more robust system would merge multiple rules for the same day.
    availability_rule = base_availability_rules[0]
    
    try:
        general_start_time_obj = time.fromisoformat(availability_rule['start_time'])
        general_end_time_obj = time.fromisoformat(availability_rule['end_time'])
    except ValueError:
        print(f"Error: Invalid time format in availability rule: {availability_rule}")
        return []


    # Combine date with time to get datetime objects
    day_start_dt = datetime.combine(target_date, general_start_time_obj)
    day_end_dt = datetime.combine(target_date, general_end_time_obj)

    # b. Represent as Time Intervals (for filtering existing events)
    # Filter appointments and time-offs for the specific provider and target date
    provider_appointments_on_date = [
        (app['start_time'], app['end_time']) for app in existing_appointments_data
        if app['provider_id'] == provider_id and app['start_time'].date() == target_date
    ]
    
    provider_time_offs_on_date = [
        (toff['start_time'], toff['end_time']) for toff in time_off_data
        if toff['provider_id'] == provider_id and \
           toff['start_time'].date() <= target_date <= toff['end_time'].date() # Handle multi-day timeoffs
    ]
    
    # Adjust multi-day time-offs to only cover the target_date
    adjusted_time_offs = []
    for off_start, off_end in provider_time_offs_on_date:
        current_off_start = datetime.combine(target_date, time.min) if off_start.date() < target_date else off_start
        current_off_end = datetime.combine(target_date, time.max) if off_end.date() > target_date else off_end
        adjusted_time_offs.append((current_off_start, current_off_end))


    # d. Generate Slots (Iterate and Check)
    slot_delta = timedelta(minutes=slot_duration_minutes)
    current_slot_start = day_start_dt

    while current_slot_start < day_end_dt:
        current_slot_end = current_slot_start + slot_delta
        if current_slot_end > day_end_dt: # Do not exceed general availability
            break

        if is_slot_available(current_slot_start, current_slot_end, 
                             provider_appointments_on_date, adjusted_time_offs):
            available_slots.append((current_slot_start, current_slot_end))
        
        current_slot_start += slot_delta # Move to the next potential slot start

    return available_slots


# --- Step 5: Example Usage in `core.py` ---
if __name__ == "__main__":
    print("--- Smart Scheduler Example ---")

    test_provider_id = 'prov1'
    slot_duration = 30

    # Scenario 1: Day with existing appointments and time off
    test_date_1 = date(2024, 7, 29) # Monday
    print(f"\nScenario 1: Finding slots for Provider {test_provider_id} on {test_date_1} (Slot duration: {slot_duration} mins)")
    
    # Modify sample data slightly for more interesting scenario 1
    sample_existing_appointments_data_sc1 = [
        {'provider_id': 'prov1', 'start_time': datetime(2024, 7, 29, 10, 0), 'end_time': datetime(2024, 7, 29, 10, 30)},
        {'provider_id': 'prov1', 'start_time': datetime(2024, 7, 29, 11, 0), 'end_time': datetime(2024, 7, 29, 11, 30)},
    ]
    sample_time_off_data_sc1 = [
        {'provider_id': 'prov1', 'start_time': datetime(2024, 7, 29, 14, 0), 'end_time': datetime(2024, 7, 29, 15, 0)}
    ]

    slots_1 = get_available_slots(
        provider_id=test_provider_id,
        target_date=test_date_1,
        provider_availability_data=sample_provider_availability_data,
        existing_appointments_data=sample_existing_appointments_data_sc1,
        time_off_data=sample_time_off_data_sc1,
        slot_duration_minutes=slot_duration
    )

    if slots_1:
        print("Available slots:")
        for start, end in slots_1:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("No slots available.")

    # Scenario 2: A clear day (e.g., a different Monday with no conflicts)
    test_date_2 = date(2024, 8, 5) # Also a Monday
    print(f"\nScenario 2: Finding slots for Provider {test_provider_id} on {test_date_2} (Clear Day)")
    slots_2 = get_available_slots(
        provider_id=test_provider_id,
        target_date=test_date_2,
        provider_availability_data=sample_provider_availability_data,
        existing_appointments_data=[], # No appointments on this day
        time_off_data=[],             # No time off on this day
        slot_duration_minutes=slot_duration
    )
    if slots_2:
        print("Available slots:")
        for start, end in slots_2:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("No slots available.")

    # Scenario 3: Day with general availability but fully booked or time off
    test_date_3 = date(2024, 7, 31) # Wednesday
    print(f"\nScenario 3: Finding slots for Provider {test_provider_id} on {test_date_3} (Time off in morning)")
    # Original sample_time_off_data has time off from 10:00-12:00 for prov1 on 2024-07-31
    # Availability: 10:00 - 16:00
    slots_3 = get_available_slots(
        provider_id=test_provider_id,
        target_date=test_date_3,
        provider_availability_data=sample_provider_availability_data,
        existing_appointments_data=[], 
        time_off_data=sample_time_off_data, # Using original data with time off
        slot_duration_minutes=60
    )
    if slots_3:
        print("Available slots:")
        for start, end in slots_3:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("No slots available.")

    # Scenario 4: Day with no general availability
    test_date_4 = date(2024, 7, 30) # Tuesday
    print(f"\nScenario 4: Finding slots for Provider {test_provider_id} on {test_date_4} (No General Availability)")
    slots_4 = get_available_slots(
        provider_id=test_provider_id,
        target_date=test_date_4,
        provider_availability_data=sample_provider_availability_data,
        existing_appointments_data=[],
        time_off_data=[],
        slot_duration_minutes=slot_duration
    )
    if slots_4:
        print("Available slots:")
        for start, end in slots_4:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("No slots available.")

    # Scenario 5: Using default sample data from the top of the file
    test_date_5 = date(2024, 7, 29) # Monday
    print(f"\nScenario 5: Finding slots for Provider {test_provider_id} on {test_date_5} (Original Sample Data, 60 min slots)")
    slots_5 = get_available_slots(
        provider_id=test_provider_id,
        target_date=test_date_5,
        provider_availability_data=sample_provider_availability_data,
        existing_appointments_data=sample_existing_appointments_data, # original
        time_off_data=sample_time_off_data, # original
        slot_duration_minutes=60 # original duration
    )
    if slots_5:
        print("Available slots:")
        for start, end in slots_5:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("No slots available.")
