# Agent-to-Agent (A2A) Communication Design

## 1. Overview

The purpose of Agent-to-Agent (A2A) communication in the appointment booking system is to enable dynamic scheduling, conflict resolution, and seamless information exchange between various software agents representing users, service providers, and the core system. This facilitates a responsive and intelligent booking experience, moving beyond simple database transactions to a more interactive and automated process.

## 2. Agents Involved

-   **User Agent (UA):**
    -   **Role:** Represents the user within the system. It is responsible for handling user interactions (e.g., via voice or text through the `voice_service`), capturing user requests, preferences, and selections, and communicating these to the Master Scheduling Agent. It also presents information and confirmations back to the user.
-   **Provider Agent (PA):**
    -   **Role:** Represents the service provider. It manages the provider's schedule, availability, and preferences. Initially, the PA might be a more passive component, primarily reflecting information stored in the database (e.g., `ProviderAvailability`, `TimeOff`). In a more advanced system, it could actively manage and update the provider's calendar, accept/reject tentative bookings, or even proactively offer slots.
-   **Master Scheduling Agent (MSA):**
    -   **Role:** Acts as the central orchestrator and a "brain" for the scheduling process. It processes incoming requests from UAs, queries PAs (or the database directly) for provider availability, applies scheduling logic (from `scheduler_service`), incorporates AI-driven suggestions (from `ai_service`), resolves conflicts, and confirms bookings. It is the primary decision-maker for slot allocation and manages the overall state of appointments.

## 3. Key Communication Scenarios & Flows

### Scenario 1: User Initiates Appointment Booking

1.  **User -> UA:** User provides input (e.g., "Book a doctor's appointment for tomorrow afternoon") via voice or text.
2.  **UA -> MSA:** UA sends a `REQUEST_APPOINTMENT` message.
    -   Payload includes: `user_id`, intent (e.g., "BOOK_APPOINTMENT"), recognized entities (e.g., `service_type="doctor"`, `time_preference="tomorrow afternoon"`), and potentially context from the `ai_service` (e.g., `preferred_providers`, `suggested_duration`).
3.  **MSA -> PA/DB:** MSA queries for availability. This might involve:
    -   Direct database lookups against `ProviderAvailability`, `Appointments`, `TimeOff` tables.
    -   Sending a `QUERY_AVAILABILITY` message to relevant PAs (if PAs are active components managing their own schedules).
    -   Utilizing the `scheduler_service.get_available_slots()` function.
4.  **PA/DB -> MSA:** Availability response is sent back.
    -   Payload includes: list of available slots for the queried providers within the specified timeframes.
5.  **MSA -> UA:** MSA sends an `OFFER_SLOTS` message.
    -   Payload includes: A ranked list of available slots, potentially enriched with match scores or reasons from the `ai_service` (e.g., "Matches preferred provider and time").
6.  **User -> UA:** User selects a desired slot from the options presented.
7.  **UA -> MSA:** UA sends a `CONFIRM_SLOT` message.
    -   Payload includes: `user_id`, `selected_slot_details` (provider_id, start_time, end_time).
8.  **MSA -> PA/DB:** MSA attempts to secure the booking.
    -   This could involve creating a new record in the `Appointments` table with a "pending" or "confirmed" status.
    -   If PA is active, it might involve a `REQUEST_BOOKING` message to the PA, which then confirms.
9.  **PA/DB -> MSA:** Booking confirmation or failure is returned.
    -   Payload includes: `appointment_id` (if successful), `status` (confirmed, failed), `reason` (if failed, e.g., "slot just filled").
10. **MSA -> UA:** MSA sends a `FINAL_APPOINTMENT_CONFIRMATION` message.
    -   Payload includes: `appointment_details` (if successful) or `failure_reason`.
11. **UA -> User:** UA informs the user of the outcome (e.g., "Your appointment is confirmed," or "Sorry, that slot was just taken. Would you like to try another?").

### Scenario 2: Provider Initiates Change (e.g., New Unavailability)

1.  **Provider -> PA:** Provider updates their schedule (e.g., adds a new time-off block via a calendar interface or admin panel).
2.  **PA -> MSA:** PA sends an `UPDATE_UNAVAILABILITY` message (or MSA detects change via DB update).
    -   Payload includes: `provider_id`, `time_off_start`, `time_off_end`, `reason` (optional).
3.  **MSA:** MSA updates the provider's schedule in the database (creates/updates `TimeOff` record). It then checks for conflicts with existing confirmed appointments using logic similar to `scheduler_service`.
4.  **MSA -> UA (of affected users):** If conflicts arise, MSA sends a `NOTIFY_APPOINTMENT_CHANGE` message to the UAs of affected users.
    -   Payload includes: `user_id`, `original_appointment_details`, `reason_for_change` (e.g., "Provider became unavailable"), and potentially `suggested_reschedule_options` generated by MSA.
5.  **MSA -> PA (Optional):** MSA sends an `ACKNOWLEDGE_UPDATE` message.
    -   Payload includes: `status_of_update` (e.g., "acknowledged"), `conflicts_found_and_actions_taken`.
6.  **UA -> User:** UA informs the affected user(s) about the appointment change/cancellation and prompts for rescheduling if necessary.

### (Optional) Scenario 3: Proactive Suggestion by MSA

1.  **MSA (Internal Trigger):** MSA, through a periodic check or event (e.g., a preferred provider updates availability), identifies an opportunity for a user.
    -   Example: `ai_service` indicates `user_X` prefers `provider_Y`. `provider_Y` just opened up new slots.
2.  **MSA -> UA (of relevant user):** MSA sends a `PROACTIVE_SUGGESTION` message.
    -   Payload includes: `user_id`, `suggestion_details` (e.g., "Your preferred provider, Dr. Smith, has new availability on [date] at [time]. Would you like to book?").
3.  **UA -> User:** UA presents the suggestion to the user.
4.  **User -> UA:** User responds (e.g., "Yes, book it," or "No, thanks").
5.  **(Follows Scenario 1 from Step 7 if user accepts):** UA -> MSA (Confirm selected slot), etc.

## 4. Message Formats (Conceptual)

Messages exchanged between agents will likely be JSON objects. Each message should contain a common header and a specific payload.

**Common Message Header Fields:**

-   `message_id`: (String, UUID) Unique identifier for this specific message.
-   `correlation_id`: (String, UUID, Optional) ID of the message this is a response to, or a shared ID for a sequence of related messages in a flow.
-   `timestamp`: (String, ISO 8601 DateTime) Time the message was generated.
-   `source_agent_id`: (String) Identifier of the agent sending the message (e.g., "ua_user123", "msa_main", "pa_prov789").
-   `target_agent_id`: (String) Identifier of the agent intended to receive the message.
-   `message_type`: (String) Defines the purpose of the message (e.g., "REQUEST_APPOINTMENT", "QUERY_AVAILABILITY", "OFFER_SLOTS", "CONFIRM_SLOT", "UPDATE_UNAVAILABILITY").
-   `payload`: (Object) Data specific to the message type.

**Example Message: `REQUEST_APPOINTMENT` (UA to MSA)**

```json
{
  "message_id": "msg_uuid_1",
  "correlation_id": "flow_uuid_xyz",
  "timestamp": "2024-03-15T10:00:00Z",
  "source_agent_id": "ua_user123",
  "target_agent_id": "msa_main",
  "message_type": "REQUEST_APPOINTMENT",
  "payload": {
    "user_id": "user123",
    "request_details": {
      "service_type": "doctor",
      "time_preference": {
        "type": "flexible_date", 
        "date": "tomorrow", 
        "time_of_day": "afternoon" 
      },
      "desired_duration_minutes": 30 
    },
    "context": {
      "preferred_providers": ["prov_dr_smith", "prov_clinic_a"],
      "suggested_duration": 30 
    }
  }
}
```

**Example Message: `OFFER_SLOTS` (MSA to UA)**

```json
{
  "message_id": "msg_uuid_2",
  "correlation_id": "flow_uuid_xyz", 
  "in_reply_to": "msg_uuid_1",
  "timestamp": "2024-03-15T10:00:05Z",
  "source_agent_id": "msa_main",
  "target_agent_id": "ua_user123",
  "message_type": "OFFER_SLOTS",
  "payload": {
    "request_echo": { 
        "service_type": "doctor", 
        "time_preference": "tomorrow afternoon"
    },
    "available_slots": [
      {
        "slot_id": "slot_uuid_a",
        "provider_id": "prov_dr_smith",
        "start_time": "2024-03-16T14:00:00Z",
        "end_time": "2024-03-16T14:30:00Z",
        "match_score": 0.9, 
        "reasoning": ["Matches preferred provider", "Matches time preference"]
      },
      {
        "slot_id": "slot_uuid_b",
        "provider_id": "prov_clinic_a",
        "start_time": "2024-03-16T15:00:00Z",
        "end_time": "2024-03-16T15:30:00Z",
        "match_score": 0.7,
        "reasoning": ["Matches preferred provider"]
      }
    ],
    "suggestion_context": "Found slots based on your preferences."
  }
}
```

## 5. Communication Protocols & Transport (Considerations)

The choice of protocol and transport mechanism depends on the deployment architecture:

-   **Internal (within a monolithic backend):**
    -   **Direct Function Calls:** If all agents reside within the same process (e.g., different modules of a single application), communication can be via direct Python function/method calls. This is simple and efficient.
    -   **Internal Event Bus/System:** A lightweight publish/subscribe system within the application can decouple modules further. Python libraries like `PyPubSub` or custom event dispatchers could be used.
-   **External (if agents become microservices):**
    -   **HTTP/REST APIs:** Agents expose endpoints for synchronous request/response interactions. Suitable for direct queries or commands.
    -   **Message Queues (e.g., RabbitMQ, Kafka, Redis Streams):** For asynchronous communication, decoupling, and improved resilience. Agents publish messages to queues, and other agents subscribe to relevant topics/queues. This is ideal for event-driven flows like updates or notifications.

**Considerations:**

-   **Reliability:** Ensure messages are not lost (e.g., acknowledgments, persistent queues).
-   **Asynchronicity:** Allow agents to operate independently without waiting for immediate responses, crucial for scalability and responsiveness. Message queues inherently support this.
-   **Scalability:** The chosen mechanism should allow individual agents to scale independently if they become separate services.
-   **Complexity:** Introducing external message brokers or HTTP APIs adds setup and operational complexity compared to internal calls.

Initially, a monolithic backend might use direct calls or an internal event bus. As the system grows, transitioning to microservices with message queues could be considered.

## 6. Key Data Elements in Messages (Summary)

-   `user_id`
-   `provider_id`
-   `service_type`
-   `appointment_id`
-   `slot_details` (start_time, end_time, slot_id)
-   Time Preferences (specific dates, relative dates like "tomorrow", time ranges like "afternoon", day_of_week preferences)
-   User Preferences (as derived from `ai_service`: preferred providers, default duration, preferred time windows)
-   Status (e.g., `REQUESTED`, `OFFERED`, `SELECTED`, `CONFIRMED`, `CANCELLED_BY_USER`, `CANCELLED_BY_PROVIDER`, `COMPLETED`, `FAILED`)
-   Reason codes/messages (for failures, changes, or suggestions)
-   Match scores or ranking information for offered slots.

## 7. Error Handling & Resilience (Briefly)

-   **Timeouts:** Implement timeouts for requests between agents, especially for synchronous calls.
-   **Retries:** For transient errors (e.g., temporary network issues, a service being briefly unavailable), implement a retry mechanism with exponential backoff.
-   **Clear Error Messages:** If a request cannot be fulfilled (e.g., no slots available, provider rejects booking), the MSA should send a clear, user-friendly error message back to the UA.
-   **Idempotency:** Design message handlers to be idempotent where possible, especially for commands that modify state (e.g., booking an appointment). If a message is processed multiple times due to retries, it should not result in duplicate actions.
-   **Slot Contention:** To handle situations where a slot gets booked by another user during negotiation (between MSA offering and UA confirming):
    -   **Optimistic Locking:** When attempting to book, the MSA can check if the slot's status or version has changed since it was offered.
    -   **Transactional Steps:** If possible, use database transactions for booking. A slot could be "reserved" or "held" for a short period, though this adds complexity.
    -   The MSA should inform the UA if the selected slot is no longer available and potentially offer alternatives.
-   **Dead Letter Queues (DLQs):** If using message queues, configure DLQs to capture messages that repeatedly fail processing for later analysis.

## 8. Future Considerations

-   **More Complex Negotiation:**
    -   Allowing users/UAs to make counter-offers for appointment times if initial suggestions are not suitable.
    -   Providers/PAs being able to propose alternative slots if a requested time is not ideal.
-   **Integration with External Calendar Systems:**
    -   Allowing PAs to sync directly with providers' Google Calendar, Outlook Calendar, etc., for real-time availability and booking. This would require OAuth and API integrations.
-   **Group Appointments:** Extending the logic to handle bookings for multiple users.
-   **Resource-Based Scheduling:** Beyond just provider time, scheduling based on other resources (e.g., specific rooms, equipment).
-   **Enhanced AI:** More sophisticated AI for predicting user needs, optimizing provider schedules, and handling complex negotiation scenarios.Okay, I have created the `appointment_booking_system/docs/a2a_communication_design.md` file with the specified content.
