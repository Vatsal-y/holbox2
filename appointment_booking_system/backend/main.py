from fastapi import FastAPI

app = FastAPI(title="Appointment Booking System API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Appointment Booking System API"}

# We will include routers here later
# Assuming 'backend' is in PYTHONPATH or the execution context handles it.
# For direct execution like 'python main.py' from within 'backend/',
# the import might need to be 'from auth import auth_router'.
# However, for uvicorn run from the project root, 'from backend.auth...' is standard.
try:
    from backend.auth import auth_router
except ImportError:
    # This fallback is for cases where main.py is run directly from backend/
    # and the 'backend' package itself isn't in the path in that specific context.
    from auth import auth_router
try:
    from backend.appointments import appointments_router
except ImportError:
    # Fallback for direct execution or certain testing setups
    from appointments import appointments_router
try:
    from backend.providers import providers_router
except ImportError:
    # Fallback for direct execution or certain testing setups
    from providers import providers_router


app.include_router(auth_router.router)
app.include_router(appointments_router.router)
app.include_router(providers_router.router)
# from backend.auth import auth_router # Assuming backend is in PYTHONPATH
# app.include_router(auth_router.router)
