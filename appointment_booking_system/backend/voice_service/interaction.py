# interaction.py - Module for simulated voice interaction

def recognize_speech(audio_data_placeholder: str) -> str:
    """
    Simulates a Speech-to-Text (STT) engine.
    Takes a placeholder for audio data and returns a transcribed text.
    """
    if audio_data_placeholder == "book_appointment_test_audio":
        return "Book an appointment for me."
    elif audio_data_placeholder == "doctor_tomorrow_test_audio":
        return "I need a doctor's appointment for tomorrow."
    elif audio_data_placeholder == "haircut_today_test_audio":
        return "I want a haircut today."
    else:
        return "Sorry, I could not understand the audio."

def extract_intent(text_input: str) -> dict:
    """
    Simulates basic Natural Language Understanding (NLU) for intent extraction.
    Takes transcribed text and returns a structured intent and entities.
    """
    text_input_lower = text_input.lower()
    intent_data = {"intent": "UNKNOWN", "entities": {}}

    if "book appointment" in text_input_lower or "make an appointment" in text_input_lower:
        intent_data["intent"] = "BOOK_APPOINTMENT"

    if "doctor" in text_input_lower:
        intent_data["intent"] = "BOOK_APPOINTMENT" # Overrides if "book appointment" wasn't present but "doctor" is
        intent_data["entities"]["service_type"] = "doctor"
        if "tomorrow" in text_input_lower:
            intent_data["entities"]["date_preference"] = "tomorrow"
        elif "today" in text_input_lower:
            intent_data["entities"]["date_preference"] = "today"

    if "haircut" in text_input_lower:
        intent_data["intent"] = "BOOK_APPOINTMENT" # Overrides if "book appointment" wasn't present but "haircut" is
        intent_data["entities"]["service_type"] = "haircut"
        if "tomorrow" in text_input_lower:
            intent_data["entities"]["date_preference"] = "tomorrow"
        elif "today" in text_input_lower:
            intent_data["entities"]["date_preference"] = "today"
    
    # If BOOK_APPOINTMENT was set but no specific service, clear entities or set a general one
    if intent_data["intent"] == "BOOK_APPOINTMENT" and not intent_data["entities"]:
        # This case handles "Book an appointment for me." without further specifics yet.
        pass

    return intent_data

def speak_response(text_response: str):
    """
    Simulates a Text-to-Speech (TTS) engine.
    Prints the text response to the console.
    """
    print(f"AI Says: {text_response}")

if __name__ == "__main__":
    # Example Usage Flow 1
    print("--- Example Flow 1 ---")
    user_audio_input_1 = "doctor_tomorrow_test_audio"
    print(f"User simulated audio input: {user_audio_input_1}")

    recognized_text_1 = recognize_speech(user_audio_input_1)
    print(f"Recognized text: \"{recognized_text_1}\"")

    intent_details_1 = extract_intent(recognized_text_1)
    print(f"Extracted intent: {intent_details_1}")

    response_1 = "Unrecognized intent."
    if intent_details_1["intent"] == "BOOK_APPOINTMENT":
        entities = intent_details_1.get("entities", {})
        service = entities.get("service_type", "any service")
        date_pref = entities.get("date_preference", "any time")
        response_1 = f"Okay, I will look for a '{service}' appointment for '{date_pref}'."
    
    speak_response(response_1)
    print("-" * 20)

    # Example Usage Flow 2
    print("\n--- Example Flow 2 ---")
    user_audio_input_2 = "book_appointment_test_audio"
    print(f"User simulated audio input: {user_audio_input_2}")
    
    recognized_text_2 = recognize_speech(user_audio_input_2)
    print(f"Recognized text: \"{recognized_text_2}\"")

    intent_details_2 = extract_intent(recognized_text_2)
    print(f"Extracted intent: {intent_details_2}")

    response_2 = "Unrecognized intent."
    if intent_details_2["intent"] == "BOOK_APPOINTMENT":
        entities = intent_details_2.get("entities", {})
        service = entities.get("service_type", "any service")
        date_pref = entities.get("date_preference", "any time") # Though not specified in this audio
        response_2 = f"Okay, I will help you book an appointment. What kind of service are you looking for and when?"

    speak_response(response_2)
    print("-" * 20)

    # Example Usage Flow 3
    print("\n--- Example Flow 3 ---")
    user_audio_input_3 = "unknown_audio_sample"
    print(f"User simulated audio input: {user_audio_input_3}")

    recognized_text_3 = recognize_speech(user_audio_input_3)
    print(f"Recognized text: \"{recognized_text_3}\"")

    intent_details_3 = extract_intent(recognized_text_3) # Will be UNKNOWN
    print(f"Extracted intent: {intent_details_3}")
    
    response_3 = "I'm sorry, I didn't understand that. Could you please repeat?"
    if intent_details_3["intent"] != "UNKNOWN": # Should not happen with this input
        response_3 = "Okay." # Fallback, though should be the "Sorry..." message

    speak_response(response_3)
    print("-" * 20)

    # Example Usage Flow 4
    print("\n--- Example Flow 4 ---")
    user_audio_input_4 = "haircut_today_test_audio"
    print(f"User simulated audio input: {user_audio_input_4}")

    recognized_text_4 = recognize_speech(user_audio_input_4)
    print(f"Recognized text: \"{recognized_text_4}\"")

    intent_details_4 = extract_intent(recognized_text_4)
    print(f"Extracted intent: {intent_details_4}")

    response_4 = "Unrecognized intent."
    if intent_details_4["intent"] == "BOOK_APPOINTMENT":
        entities = intent_details_4.get("entities", {})
        service = entities.get("service_type", "any service")
        date_pref = entities.get("date_preference", "any time")
        response_4 = f"Okay, I will look for a '{service}' appointment for '{date_pref}'."

    speak_response(response_4)
    print("-" * 20)
