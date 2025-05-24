# suggestions.py - Module for AI-driven scheduling suggestions

from datetime import datetime, timedelta, date
from collections import Counter

# --- Step 2: Define Simulated Data Structures ---
mock_user_preferences = {
    "user123": {
        "user_id": "user123",
        "preferred_provider_ids": ["prov_dr_smith", "prov_clinic_a"],
        "preferred_time_slots": [
            {"start_time": "09:00", "end_time": "12:00", "days_of_week": [0, 1, 2, 3, 4]}, # Mon-Fri mornings (weekday() 0-4)
            {"start_time": "14:00", "end_time": "17:00", "days_of_week": [0, 2]}    # Mon, Wed afternoons
        ],
        "preferred_days_of_week": [0, 2, 4], # Mon, Wed, Fri
        "default_appointment_duration": 45, # minutes
    },
    "user456": {
        "user_id": "user456",
        "preferred_provider_ids": ["prov_dr_jones"],
        "default_appointment_duration": 60,
        "preferred_time_slots": [], # No specific time slots, implies general day preference
        "preferred_days_of_week": [0, 1, 2, 3, 4, 5, 6], # Any day
    }
}

mock_appointment_history = {
    "user123": [
        {"provider_id": "prov_dr_smith", "service_type": "check-up", "start_time": datetime(2023, 1, 10, 10, 0), "end_time": datetime(2023, 1, 10, 10, 30)},
        {"provider_id": "prov_dr_smith", "service_type": "check-up", "start_time": datetime(2023, 7, 15, 10, 0), "end_time": datetime(2023, 7, 15, 10, 30)},
        {"provider_id": "prov_clinic_a", "service_type": "physiotherapy", "start_time": datetime(2023, 8, 20, 14, 0), "end_time": datetime(2023, 8, 20, 14, 45)},
        {"provider_id": "prov_dr_x", "service_type": "check-up", "start_time": datetime(2022, 12, 1, 10, 0), "end_time": datetime(2022, 12, 1, 10, 30)}, # Another provider for check-up
    ],
    "user456": [
        {"provider_id": "prov_dr_jones", "service_type": "consultation", "start_time": datetime(2023, 5, 5, 9, 0), "end_time": datetime(2023, 5, 5, 10, 0)},
        {"provider_id": "prov_dr_jones", "service_type": "follow-up", "start_time": datetime(2023, 11, 10, 9, 0), "end_time": datetime(2023, 11, 10, 9, 45)},

    ]
}

# --- Step 3: Implement Suggestion Functions ---

def get_preferred_providers(user_id: str, service_type: str = None) -> list[str]:
    """
    Suggests preferred providers for a user, optionally filtered by service type.
    Combines explicit preferences with historical usage.
    """
    user_prefs = mock_user_preferences.get(user_id, {})
    user_history = mock_appointment_history.get(user_id, [])

    preferred_providers = list(user_prefs.get("preferred_provider_ids", []))
    
    historical_providers_counts = Counter()
    for appt in user_history:
        if service_type is None or appt.get("service_type") == service_type:
            historical_providers_counts[appt["provider_id"]] += 1
    
    # Add historically used providers, ordered by frequency, then by original preference
    # Providers mentioned in preferences first, then others from history
    
    # Create a combined list, ensuring preferred ones come first if also in history
    combined_providers = []
    
    # Add preferred providers first, maintaining their order
    for p_id in preferred_providers:
        combined_providers.append(p_id)
        
    # Add historical providers not already in the list, by frequency
    for p_id, count in historical_providers_counts.most_common():
        if p_id not in combined_providers:
            combined_providers.append(p_id)
            
    # If no preferences and no history, return empty
    if not combined_providers and not historical_providers_counts:
        return []

    # Simple re-ordering: if a provider is in both, ensure it's earlier.
    # A more sophisticated ranking could be applied here.
    # For now, we sort history providers by frequency and append those not in explicit prefs.
    
    # Let's refine: explicit preferences are primary. Historical frequencies help sort *within* those or add new ones.
    
    # Start with explicit preferred providers
    final_ordered_list = list(user_prefs.get("preferred_provider_ids", []))
    
    # Get historical providers sorted by frequency
    historically_sorted = [p_id for p_id, count in historical_providers_counts.most_common()]
    
    # Add historical providers to the list if they are not already there
    for p_id in historically_sorted:
        if p_id not in final_ordered_list:
            final_ordered_list.append(p_id)
            
    return final_ordered_list


def get_suggested_duration(user_id: str, service_type: str = None) -> int:
    """
    Suggests an appointment duration based on history for the service type,
    user preferences, or a system default.
    """
    user_prefs = mock_user_preferences.get(user_id, {})
    user_history = mock_appointment_history.get(user_id, [])
    
    SYSTEM_DEFAULT_DURATION = 60 # Fallback default

    if service_type:
        durations_for_service = []
        for appt in user_history:
            if appt.get("service_type") == service_type:
                duration = (appt["end_time"] - appt["start_time"]).total_seconds() / 60
                durations_for_service.append(int(duration))
        
        if durations_for_service:
            # Return the most common duration for this service type
            count = Counter(durations_for_service)
            return count.most_common(1)[0][0]

    if "default_appointment_duration" in user_prefs:
        return user_prefs["default_appointment_duration"]
        
    return SYSTEM_DEFAULT_DURATION


def get_preferred_time_windows(user_id: str, target_date: date) -> list[dict]:
    """
    Gets preferred time windows for a user on a specific target date.
    """
    user_prefs = mock_user_preferences.get(user_id, {})
    if not user_prefs:
        return [{"start_time": "09:00", "end_time": "17:00"}] # Default broad window if no user prefs

    target_weekday = target_date.weekday() # Monday is 0, Sunday is 6

    preferred_days = user_prefs.get("preferred_days_of_week", [])
    
    # If the target day is not in their generally preferred days, return empty or default.
    # For this implementation, if preferred_days_of_week is set and target_date's weekday is not in it,
    # assume no specific slots are preferred for that day *unless* preferred_time_slots override this.
    
    relevant_slots = []
    user_time_slots = user_prefs.get("preferred_time_slots", [])

    explicitly_preferred_day = target_weekday in preferred_days if preferred_days else True


    for slot in user_time_slots:
        if target_weekday in slot.get("days_of_week", []):
            relevant_slots.append({"start_time": slot["start_time"], "end_time": slot["end_time"]})
    
    if relevant_slots:
        return relevant_slots

    # If no specific slots for that day, but the day itself is generally preferred, return a broad window.
    if explicitly_preferred_day and not user_time_slots: # User likes this day but has no specific slots listed for it
        return [{"start_time": "09:00", "end_time": "17:00"}] # Default broad window for a preferred day

    # If the day is not in preferred_days_of_week AND no specific slots override this, return empty.
    if not explicitly_preferred_day:
         return []


    return [] # Default to no specific windows if no conditions met

# --- Step 4: Example Usage ---
if __name__ == "__main__":
    print(f"--- User user123 ---")
    print(f"Preferred providers (no service specified): {get_preferred_providers('user123')}")
    print(f"Preferred providers for 'check-up': {get_preferred_providers('user123', 'check-up')}")
    print(f"Preferred providers for 'physiotherapy': {get_preferred_providers('user123', 'physiotherapy')}")
    print(f"Suggested duration (no service): {get_suggested_duration('user123')} mins")
    print(f"Suggested duration for 'check-up': {get_suggested_duration('user123', 'check-up')} mins")
    print(f"Suggested duration for 'physiotherapy': {get_suggested_duration('user123', 'physiotherapy')} mins")
    
    # Test dates
    monday = date(2024, 7, 29) # weekday() is 0
    tuesday = date(2024, 7, 30) # weekday() is 1
    wednesday = date(2024, 7, 31) # weekday() is 2

    print(f"Preferred time windows for date {monday} (Monday): {get_preferred_time_windows('user123', monday)}")
    print(f"Preferred time windows for date {tuesday} (Tuesday): {get_preferred_time_windows('user123', tuesday)}") # User123 doesn't prefer Tuesday in preferred_days_of_week, but has morning slot
    print(f"Preferred time windows for date {wednesday} (Wednesday): {get_preferred_time_windows('user123', wednesday)}")


    print(f"\n--- User user456 ---")
    print(f"Preferred providers: {get_preferred_providers('user456')}")
    print(f"Preferred providers for 'consultation': {get_preferred_providers('user456', 'consultation')}")
    print(f"Suggested duration (no service): {get_suggested_duration('user456')} mins")
    print(f"Suggested duration for 'consultation': {get_suggested_duration('user456', 'consultation')} mins")
    print(f"Suggested duration for 'follow-up': {get_suggested_duration('user456', 'follow-up')} mins")
    print(f"Preferred time windows for date {monday} (Monday): {get_preferred_time_windows('user456', monday)}")
    print(f"Preferred time windows for date {tuesday} (Tuesday): {get_preferred_time_windows('user456', tuesday)}")

    print(f"\n--- User non_existent_user ---")
    print(f"Preferred providers: {get_preferred_providers('non_existent_user')}")
    print(f"Suggested duration: {get_suggested_duration('non_existent_user')} mins")
    print(f"Preferred time windows for date {monday} (Monday): {get_preferred_time_windows('non_existent_user', monday)}")
