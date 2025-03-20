import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "francoismogaka@gmail.com"
SMTP_PASSWORD = "drfrrdchnybdchkh"

def send_email(sender: str, recipients: list, subject: str, message: str):
    if not recipients:
        return  # No one to notify

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(sender, recipients, msg.as_string())
        print(f"Email sent to {recipients}")
    except Exception as e:
        print(f"Error sending email: {e}")
