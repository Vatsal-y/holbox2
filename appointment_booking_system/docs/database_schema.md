# PostgreSQL Database Schema for Appointment Booking System

This document outlines the database schema for the appointment booking system.

## Table: Users

Stores information about users of the system.

| Column Name     | Data Type        | Constraints                                                                 | Description                               |
|-----------------|------------------|-----------------------------------------------------------------------------|-------------------------------------------|
| `user_id`       | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                      | Unique identifier for the user            |
| `name`          | VARCHAR(255)     | NOT NULL                                                                    | Name of the user                          |
| `email`         | VARCHAR(255)     | UNIQUE, NOT NULL                                                            | Email address of the user (for login)     |
| `phone_number`  | VARCHAR(50)      | UNIQUE, NOT NULL                                                            | Phone number of the user                  |
| `password_hash` | TEXT             | NOT NULL                                                                    | Hashed password for user authentication   |
| `created_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                         | Timestamp of user creation                |
| `updated_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                         | Timestamp of last user update             |

**Relationships:**
*   One-to-Many with `Appointments` (a user can have multiple appointments)
*   One-to-One with `UserPreferences` (a user has one preference set)

**Potential Indexes:**
*   `idx_users_email` on `email`
*   `idx_users_phone_number` on `phone_number`

---

## Table: ServiceProviders

Stores information about service providers.

| Column Name      | Data Type        | Constraints                                                                 | Description                                     |
|------------------|------------------|-----------------------------------------------------------------------------|-------------------------------------------------|
| `provider_id`    | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                      | Unique identifier for the service provider      |
| `name`           | VARCHAR(255)     | NOT NULL                                                                    | Name of the service provider                    |
| `service_type`   | VARCHAR(255)     | NOT NULL                                                                    | Type of service offered (e.g., "Doctor")      |
| `email`          | VARCHAR(255)     | UNIQUE, NOT NULL                                                            | Email address of the provider                   |
| `phone_number`   | VARCHAR(50)      | UNIQUE, NOT NULL                                                            | Phone number of the provider                    |
| `address`        | TEXT             |                                                                             | Physical address of the provider (optional)     |
| `created_at`     | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                         | Timestamp of provider record creation           |
| `updated_at`     | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                         | Timestamp of last provider record update        |

**Relationships:**
*   One-to-Many with `Appointments` (a provider can have multiple appointments)
*   One-to-Many with `ProviderAvailability` (a provider has multiple availability slots)
*   One-to-Many with `TimeOff` (a provider can have multiple time-off entries)

**Potential Indexes:**
*   `idx_service_providers_email` on `email`
*   `idx_service_providers_phone_number` on `phone_number`
*   `idx_service_providers_service_type` on `service_type`

---

## Table: Appointments

Stores details of appointments made by users with service providers.

| Column Name           | Data Type        | Constraints                                                                                             | Description                                                                 |
|-----------------------|------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `appointment_id`      | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                                                  | Unique identifier for the appointment                                       |
| `user_id`             | UUID             | NOT NULL, FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE                       | Foreign key referencing the user who booked                                 |
| `provider_id`         | UUID             | NOT NULL, FOREIGN KEY (`provider_id`) REFERENCES `ServiceProviders`(`provider_id`) ON DELETE CASCADE    | Foreign key referencing the service provider                                |
| `start_time`          | TIMESTAMP WITH TIME ZONE | NOT NULL                                                                                                | Start date and time of the appointment                                      |
| `end_time`            | TIMESTAMP WITH TIME ZONE | NOT NULL                                                                                                | End date and time of the appointment                                        |
| `status`              | VARCHAR(50)      | NOT NULL, CHECK (`status` IN ('scheduled', 'confirmed', 'cancelled_by_user', 'cancelled_by_provider', 'completed')) | Current status of the appointment                                           |
| `service_description` | TEXT             |                                                                                                         | Description of the service for this appointment (optional)                  |
| `notes_user`          | TEXT             |                                                                                                         | Notes from the user for the appointment (optional)                          |
| `notes_provider`      | TEXT             |                                                                                                         | Notes from the provider for the appointment (optional)                      |
| `created_at`          | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                                                     | Timestamp of appointment creation                                           |
| `updated_at`          | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                                                     | Timestamp of last appointment update                                        |

**Relationships:**
*   Many-to-One with `Users`
*   Many-to-One with `ServiceProviders`

**Potential Indexes:**
*   `idx_appointments_user_id` on `user_id`
*   `idx_appointments_provider_id` on `provider_id`
*   `idx_appointments_start_time` on `start_time`
*   `idx_appointments_end_time` on `end_time`
*   `idx_appointments_status` on `status`
*   `idx_appointments_provider_id_start_time` on (`provider_id`, `start_time`) for quick provider schedule lookup

---

## Table: ProviderAvailability

Stores the general recurring availability of service providers.

| Column Name       | Data Type        | Constraints                                                                                             | Description                                                                 |
|-------------------|------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `availability_id` | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                                                  | Unique identifier for the availability slot                                 |
| `provider_id`     | UUID             | NOT NULL, FOREIGN KEY (`provider_id`) REFERENCES `ServiceProviders`(`provider_id`) ON DELETE CASCADE    | Foreign key referencing the service provider                                |
| `day_of_week`     | INTEGER          | NOT NULL, CHECK (`day_of_week` BETWEEN 0 AND 6)                                                         | Day of the week (0 for Sunday, 1 for Monday, ..., 6 for Saturday)           |
| `start_time`      | TIME WITHOUT TIME ZONE | NOT NULL                                                                                                | Start time of the availability slot (e.g., '09:00:00')                      |
| `end_time`        | TIME WITHOUT TIME ZONE | NOT NULL                                                                                                | End time of the availability slot (e.g., '17:00:00')                        |
| `is_active`       | BOOLEAN          | NOT NULL, DEFAULT TRUE                                                                                  | Whether this availability slot is currently active                          |
| `valid_from`      | DATE             |                                                                                                         | Date from which this availability is valid (optional)                       |
| `valid_until`     | DATE             |                                                                                                         | Date until which this availability is valid (optional)                      |

**Relationships:**
*   Many-to-One with `ServiceProviders`

**Potential Indexes:**
*   `idx_provider_availability_provider_id` on `provider_id`
*   `idx_provider_availability_day_of_week` on `day_of_week`
*   `idx_provider_availability_provider_id_day_of_week` on (`provider_id`, `day_of_week`, `start_time`, `end_time`) for efficient lookup

---

## Table: TimeOff

Stores specific one-off unavailability for service providers (e.g., holidays, breaks).

| Column Name   | Data Type        | Constraints                                                                                             | Description                                                                 |
|---------------|------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `time_off_id` | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                                                  | Unique identifier for the time-off entry                                    |
| `provider_id` | UUID             | NOT NULL, FOREIGN KEY (`provider_id`) REFERENCES `ServiceProviders`(`provider_id`) ON DELETE CASCADE    | Foreign key referencing the service provider                                |
| `start_time`  | TIMESTAMP WITH TIME ZONE | NOT NULL                                                                                                | Start date and time of the time-off period                                  |
| `end_time`    | TIMESTAMP WITH TIME ZONE | NOT NULL                                                                                                | End date and time of the time-off period                                    |
| `reason`      | TEXT             |                                                                                                         | Reason for the time off (optional, e.g., "Vacation")                        |

**Relationships:**
*   Many-to-One with `ServiceProviders`

**Potential Indexes:**
*   `idx_time_off_provider_id` on `provider_id`
*   `idx_time_off_start_time_end_time` on (`start_time`, `end_time`)
*   `idx_time_off_provider_id_start_time_end_time` on (`provider_id`, `start_time`, `end_time`) for checking conflicts

---

## Table: UserPreferences

Stores user-specific preferences for the AI booking assistant.

| Column Name                   | Data Type        | Constraints                                                                                         | Description                                                                                                |
|-------------------------------|------------------|-----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| `preference_id`               | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid()                                                              | Unique identifier for the preference entry                                                                 |
| `user_id`                     | UUID             | NOT NULL, UNIQUE, FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE            | Foreign key referencing the user                                                                           |
| `preferred_provider_ids`      | JSONB            |                                                                                                     | List of preferred provider_ids (optional)                                                                  |
| `preferred_time_slots`        | JSONB            |                                                                                                     | Preferred time slots (e.g., `[{"start_time": "09:00", "end_time": "12:00", "day_of_week": [1,2,3,4,5]}]`) (optional) |
| `preferred_days_of_week`      | JSONB            |                                                                                                     | List of preferred days of the week [0-6] (optional)                                                        |
| `default_appointment_duration`| INTEGER          |                                                                                                     | Default duration for appointments in minutes (e.g., 30, 60) (optional)                                     |
| `last_updated`                | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                                             | Timestamp of last preference update                                                                        |

**Relationships:**
*   One-to-One with `Users`

**Potential Indexes:**
*   `idx_user_preferences_user_id` on `user_id` (already unique, but good for FK lookup)
*   Consider GIN indexes on JSONB columns if specific keys/elements within them are frequently queried:
    *   `idx_user_preferences_preferred_provider_ids` on `preferred_provider_ids` using `jsonb_path_ops`
    *   `idx_user_preferences_preferred_days_of_week` on `preferred_days_of_week` using `jsonb_path_ops`

---

**General Notes on `updated_at` columns:**
To automatically update the `updated_at` columns upon modification, a trigger function should be created and applied to each table:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Example for the Users table:
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Similar triggers should be created for ServiceProviders, Appointments, and UserPreferences tables.
```

**UUID Generation:**
The `gen_random_uuid()` function requires the `pgcrypto` extension to be enabled in PostgreSQL.
```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

This schema provides a comprehensive structure for the appointment booking system.
Further refinements and specific index strategies can be developed based on query patterns and performance testing.
