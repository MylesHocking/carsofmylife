from app.utils.email_utils import send_simple_message
from app.config import MAILGUN_DOMAIN, MAILGUN_API_KEY

def send_notification_email(recipient, subject, text):
    print(f'Sending email to {recipient} with subject {subject} and text {text}')
    return send_simple_message(MAILGUN_DOMAIN, MAILGUN_API_KEY, recipient, subject, text)