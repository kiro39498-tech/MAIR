import sys
import os
import smtplib

# Add backend directory to sys.path so we can import from config and services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings
from services.notification_service import _send_email

def test_smtp_configuration():
    print("Testing SMTP configuration...")
    print(f"Host: {settings.smtp_host}")
    print(f"Port: {settings.smtp_port}")
    print(f"Username: {settings.smtp_username}")
    print(f"From: {settings.notify_email_from}")
    print(f"To: {settings.notify_email_to}")
    
    if not settings.smtp_username or not settings.smtp_password:
        print("\nERROR: SMTP_USERNAME or SMTP_PASSWORD is not set in .env")
        print("Please configure them to run this test.")
        return
        
    subject = "Test — Material Planning Agent"
    body = "If you're reading this, SMTP is configured correctly."
    
    try:
        _send_email(
            to_email=settings.notify_email_to,
            subject=subject,
            body_text=body
        )
        print("\nSUCCESS: Test email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"\nFAILURE: SMTP protocol error occurred:")
        print(e)
    except Exception as e:
        print(f"\nFAILURE: An unexpected error occurred:")
        print(e)

if __name__ == "__main__":
    test_smtp_configuration()
