from app.utils.email_utils import send_simple_message, send_html_message
from app.config import MAILGUN_DOMAIN, MAILGUN_API_KEY

def send_notification_email_old(recipient, subject, text):
    print(f'Sending email to {recipient} with subject {subject} and text {text}')
    return send_simple_message(MAILGUN_DOMAIN, MAILGUN_API_KEY, recipient, subject, text)

def send_notification_email(recipient, subject, text, user_id):
    print(f'Sending email to {recipient} with subject {subject} and text {text}')

    # Prepare the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-content {{
                font-family: sans-serif;
                font-size: 16px;
                line-height: 1.5;
            }}
            body {{
                font-family: 'Arial Black', sans-serif;
                color: #000;
                margin: 0;
                -webkit-font-smoothing: antialiased;
            }}
            header {{
                background: linear-gradient( #dc534b, #a50308);
                text-align: center; /* Center content in the header */
                padding: 10px 0; /* Add some padding */
            }}
            footer {{
                background: linear-gradient( #ae0507, #e55c54);
                width: 100%;
                padding-bottom: 40px;
                padding-top: 40px;
                margin-top: 20px;
            }}
            .footer a {{
                margin-left: 40px;
                color: black;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="App">
            <div class="main-container">
                <header>
                    <a href="https://carsofmy.life/chart/">
                        <img src="https://carsofmy.life/static/media/transparent_logo.cc9d07b48032a71a20a6.png" alt="Cars of My Life Logo" style="height: 116px; margin: auto;" />
                    </a>
                </header>
                <div class="email-content">
                    {text}  <!-- Dynamically insert the notification message -->
                </div>
                <footer style="text-align: center; padding: 20px; font-size: 12px;">
                <p>© 2023 Cars of My Life. All rights reserved.</p>
                <p>Contact us at: <a href="mailto:support@carsofmylife.com">support@carsofmylife.com</a></p>
                <p><a href="https://www.carsofmy.life/user/{user_id}">Unsubscribe to Email Notifications</a></p>
            </footer>
            </div>
        </div>
    </body>
    </html>
    """

    # Send the email with HTML content
    return send_html_message(MAILGUN_DOMAIN, MAILGUN_API_KEY, recipient, subject, text, html_content)
