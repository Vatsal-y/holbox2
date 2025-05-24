import uvicorn
import os

if __name__ == "__main__":
    # This script is intended to be run from the 'appointment_booking_system/backend/' directory.
    # Uvicorn will look for 'main:app' in the current working directory.
    # Ensure PYTHONPATH is set up correctly if running from elsewhere,
    # or adjust the 'main:app' string.
    
    # Get the directory of the current script (run.py)
    # SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Change current working directory to the directory of main.py if necessary,
    # but uvicorn typically handles this if main.py is in the CWD.
    # For this project structure, if you run `python run.py` from within the `backend` directory,
    # `main.py` should be found correctly.

    # The `app_dir` argument can explicitly tell uvicorn where to look for the app.
    # However, the string "main:app" assumes main.py is in the Python path or CWD.
    # If main.py is in the same directory as run.py (i.e., backend/), it's fine.
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
