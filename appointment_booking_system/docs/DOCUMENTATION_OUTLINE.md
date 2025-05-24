# Code Documentation Outline

## 1. Introduction
- Project overview, goals, and key features.
- Link to the main project `README.md`.

## 2. Project Structure
- Overview of main directories: `backend/`, `frontend/`, `docs/`, `tests/`.
- Brief purpose of each directory.

## 3. Backend Documentation
### 3.1. API Documentation
- Accessing auto-generated FastAPI documentation (Swagger UI at `/docs`, ReDoc at `/redoc`).
- Overview of major API modules/routers:
  - `auth_router.py` (Authentication: signup, login)
  - `appointments_router.py` (Appointment management: create, view, cancel)
  - `providers_router.py` (Provider actions: view availability)
- Authentication: JWT-based, `oauth2_scheme`.
### 3.2. Modules Overview
- `backend/auth/`: User registration, login, token management, password hashing.
- `backend/scheduler_service/core.py`: Core logic for finding available appointment slots.
- `backend/ai_service/suggestions.py`: Logic for suggesting providers, durations, and preferred times.
- `backend/notification_service/email_service.py`: Email notification sending (currently via local SMTP debug server).
- `backend/voice_service/interaction.py`: Simulated voice interaction flow (conceptual).
### 3.3. Database Schema
- Link to `docs/database_schema.md`.
- Brief explanation of key tables (Users, ServiceProviders, Appointments, ProviderAvailability, UserPreferences) and their relationships.
### 3.4. Configuration
- Main configuration in `backend/config.py` (e.g., email server settings).
- JWT settings in `backend/auth/auth_utils.py` (should be moved to config).
- Future: Use of environment variables.
### 3.5. Running the Backend
- Prerequisites (Python, pip).
- Installing dependencies: `pip install -r backend/requirements.txt`.
- Running the development server: `python backend/run.py`.
### 3.6. Testing
- Framework: `pytest`.
- Running tests: `pytest` command from the project root.
- Test structure: `tests/backend/` mirroring the backend structure.
- Current coverage focus: `scheduler_service.core.get_available_slots`.
- `pytest.ini` for configuration.

## 4. Frontend Documentation
- Overview of the placeholder HTML structure in `frontend/`.
- Link to `frontend/README.md`.
- Intended future framework (e.g., React, Vue, Angular - to be decided).
- Interaction with the backend API (general principles).

## 5. Agent-to-Agent (A2A) Communication
- Link to `docs/a2a_communication_design.md` for conceptual design.

## 6. Deployment (Future Considerations)
- Dockerization.
- Cloud platform options (e.g., AWS, Google Cloud, Azure).
- Database migration strategies.

## 7. Contributing (Future Considerations)
- Coding style guidelines.
- Branching strategy.
- Pull request process.
