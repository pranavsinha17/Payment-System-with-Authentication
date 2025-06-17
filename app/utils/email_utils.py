import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(subject: str, body: str, to_email: str):
    message = Mail(
        from_email='pranav.sinha17@gmail.com',
        to_emails=to_email,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent to {to_email}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")