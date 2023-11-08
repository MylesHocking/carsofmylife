# utils/email_utils.py
import requests

def send_simple_message(domain, api_key, recipient, subject, text):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"Excited User <mailgun@{domain}>",
            "to": recipient,
            "subject": subject,
            "text": text
        }
    )
