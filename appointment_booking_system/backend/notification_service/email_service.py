# email_service.py - Module for sending email notifications

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Assuming 'backend' is in PYTHONPATH or structure allows this.
# If running this script directly for testing, this might need adjustment
# or config.py needs to be in the same directory.
try:
    from backend import config
except ImportError:
    # This fallback is for direct execution if backend module is not found in path
    # For the __main__ block, we'll handle this more directly.
    import sys
    import os
    # Add the parent directory of 'backend' to sys.path if 'backend.config' is not found
    # This is a common pattern for scripts inside packages that need to import siblings or parents
    # For the subtask, we are asked to assume `from backend import config` is fine.
    # However, for robust __main__ execution, some path manipulation might be needed
    # depending on how the script is run.
    # For now, we'll rely on the primary import and handle __main__ separately if needed.
    print("Warning: Could not import 'from backend import config'. Attempting direct import for 'config'.")
    try:
        # This assumes config.py is in the same directory or PYTHONPATH allows direct import
        import config as backend_config_direct 
        config = backend_config_direct
    except ImportError:
        print("Error: config.py not found. Please ensure it's in the backend directory and accessible.")
        # A more robust solution for direct script execution would be to adjust sys.path
        # For example:
        # SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        # PARENT_DIR = os.path.dirname(SCRIPT_DIR) # This should be 'backend'
        # GRANDPARENT_DIR = os.path.dirname(PARENT_DIR) # This should be 'appointment_booking_system'
        # if GRANDPARENT_DIR not in sys.path:
        #    sys.path.append(GRANDPARENT_DIR)
        # from backend import config # Then this should work
        sys.exit(1) # Exit if config cannot be loaded


def send_email(recipient_email: str, subject: str, body_html: str, body_text: str = None):
    """
    Sends an email using a local SMTP debugging server.

    Args:
        recipient_email (str): The email address of the recipient.
        subject (str): The subject of the email.
        body_html (str): The HTML content of the email.
        body_text (str, optional): The plain text content of the email. Defaults to None.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config.SENDER_EMAIL
    msg['To'] = recipient_email

    if body_text:
        msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    try:
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
            server.sendmail(config.SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email} with subject '{subject}'")
    except ConnectionRefusedError:
        print(f"Error: Connection refused. Ensure the SMTP server is running at {config.EMAIL_HOST}:{config.EMAIL_PORT}")
    except Exception as e:
        print(f"Error sending email: {e}")

# --- Step 4: Define Email Templates (Simple Strings) ---
CONFIRMATION_EMAIL_HTML_TEMPLATE = """
<html><body>
<h2>Appointment Confirmation</h2>
<p>Dear {user_name},</p>
<p>Your appointment for <b>{service_name}</b> with <b>{provider_name}</b> on <b>{appointment_date}</b> at <b>{appointment_time}</b> is confirmed.</p>
<p>Thank you!</p>
</body></html>
"""

CANCELLATION_EMAIL_HTML_TEMPLATE = """
<html><body>
<h2>Appointment Cancellation Notice</h2>
<p>Dear {user_name},</p>
<p>We regret to inform you that your appointment for <b>{service_name}</b> with <b>{provider_name}</b> on <b>{appointment_date}</b> at <b>{appointment_time}</b> has been cancelled.</p>
<p>Reason: {cancellation_reason}</p>
<p>Please contact us to reschedule.</p>
</body></html>
"""

# --- Step 5: Implement Notification Functions ---
def send_appointment_confirmation_email(user_email: str, user_name: str, appointment_details: dict):
    """
    Sends an appointment confirmation email.

    Args:
        user_email (str): Recipient's email address.
        user_name (str): Recipient's name.
        appointment_details (dict): Contains service_name, provider_name, appointment_date, appointment_time.
    """
    subject = "Appointment Confirmation"
    body_html = CONFIRMATION_EMAIL_HTML_TEMPLATE.format(
        user_name=user_name,
        service_name=appointment_details.get('service_name', 'N/A'),
        provider_name=appointment_details.get('provider_name', 'N/A'),
        appointment_date=appointment_details.get('appointment_date', 'N/A'),
        appointment_time=appointment_details.get('appointment_time', 'N/A')
    )
    # Simple plain text version (can be improved)
    body_text = (
        f"Dear {user_name},\n\n"
        f"Your appointment for {appointment_details.get('service_name', 'N/A')} with {appointment_details.get('provider_name', 'N/A')} "
        f"on {appointment_details.get('appointment_date', 'N/A')} at {appointment_details.get('appointment_time', 'N/A')} is confirmed.\n\n"
        f"Thank you!"
    )
    send_email(user_email, subject, body_html, body_text)

def send_appointment_cancellation_email(user_email: str, user_name: str, appointment_details: dict, cancellation_reason: str):
    """
    Sends an appointment cancellation email.

    Args:
        user_email (str): Recipient's email address.
        user_name (str): Recipient's name.
        appointment_details (dict): Contains service_name, provider_name, appointment_date, appointment_time.
        cancellation_reason (str): Reason for cancellation.
    """
    subject = "Appointment Cancellation"
    body_html = CANCELLATION_EMAIL_HTML_TEMPLATE.format(
        user_name=user_name,
        service_name=appointment_details.get('service_name', 'N/A'),
        provider_name=appointment_details.get('provider_name', 'N/A'),
        appointment_date=appointment_details.get('appointment_date', 'N/A'),
        appointment_time=appointment_details.get('appointment_time', 'N/A'),
        cancellation_reason=cancellation_reason
    )
    # Simple plain text version
    body_text = (
        f"Dear {user_name},\n\n"
        f"We regret to inform you that your appointment for {appointment_details.get('service_name', 'N/A')} with {appointment_details.get('provider_name', 'N/A')} "
        f"on {appointment_details.get('appointment_date', 'N/A')} at {appointment_details.get('appointment_time', 'N/A')} has been cancelled.\n"
        f"Reason: {cancellation_reason}\n\n"
        f"Please contact us to reschedule."
    )
    send_email(user_email, subject, body_html, body_text)


# --- Step 6: Example Usage and Local SMTP Server Info ---
if __name__ == "__main__":
    print("To test, run a local SMTP debugging server in another terminal: python -m smtpd -c DebuggingServer -n localhost:1025")
    
    # Attempt to use the primary config import, but fall back for direct script execution
    # This is to ensure __main__ works when `python notification_service/email_service.py` is run
    # from the `backend` directory.
    try:
        from backend import config as main_config
    except ImportError:
        print("Running in __main__: Could not import 'from backend import config'. Attempting relative import for 'config'.")
        # This assumes config.py is in the parent directory relative to this script's location
        # when this script is in notification_service/
        import os
        import sys
        # Get the directory of the current script
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (which should be 'backend' if script is in 'notification_service')
        PARENT_DIR = os.path.dirname(SCRIPT_DIR)
        # Add the grandparent directory (which should be 'appointment_booking_system') to sys.path
        # to allow 'from backend import config'
        GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
        if GRANDPARENT_DIR not in sys.path:
            sys.path.insert(0, GRANDPARENT_DIR) # Prepend to path
        
        try:
            from backend import config as main_config
            # Overwrite the global 'config' for this __main__ block if it was direct_config before
            config = main_config 
        except ImportError as e:
            print(f"Fatal Error in __main__: Could not import config. Ensure config.py is in backend/ and appointment_booking_system is in PYTHONPATH. Details: {e}")
            sys.exit(1)


    sample_appointment_details = {
        'service_name': 'Dental Checkup',
        'provider_name': 'Dr. Smile',
        'appointment_date': '2024-08-15',
        'appointment_time': '10:00 AM'
    }
    sample_user_email = "testuser@example.com"
    sample_user_name = "Test User"

    print("\nAttempting to send confirmation email...")
    send_appointment_confirmation_email(
        user_email=sample_user_email,
        user_name=sample_user_name,
        appointment_details=sample_appointment_details
    )

    sample_cancellation_reason = "Provider unavailable due to an emergency."
    print("\nAttempting to send cancellation email...")
    send_appointment_cancellation_email(
        user_email=sample_user_email,
        user_name=sample_user_name,
        appointment_details=sample_appointment_details,
        cancellation_reason=sample_cancellation_reason
    )

    print("\nCheck the output of your local SMTP debugging server.")
