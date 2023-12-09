# utils/email_utils.py
import requests

def send_simple_message(domain, api_key, recipient, subject, text):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"CarsOfMy.Life <mailgun@{domain}>",
            "to": recipient,
            "subject": subject,
            "text": text
        }
    )

def send_html_message(domain, api_key, recipient, subject, text, html):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"CarsOfMy.Life <mailgun@{domain}>",
            "to": recipient,
            "subject": subject,
            "text": text,
            "html": html  
        }
    )
