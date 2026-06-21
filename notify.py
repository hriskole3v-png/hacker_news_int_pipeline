import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_digest_email(digest_md, recipient=None, subject=None):
    """
    Send the digest via email. Stubbed by default: prints instead of sending
    unless SMTP credentials are present in the environment.

    To enable real sending, set EMAIL_USER, EMAIL_PASS, and SMTP_SERVER.
    """
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    recipient = recipient or os.getenv("EMAIL_TO", sender)
    subject = subject or "Daily Hacker News Tech Digest"

    # Stub mode: no credentials configured
    if not sender or not password:
        print("[notify] Email not configured — digest ready to send.")
        print(f"[notify] Would send to: {recipient or 'recipient@example.com'}")
        print(f"[notify] Subject: {subject}")
        return False

    # Real send path (wired, ready when credentials are provided)
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(digest_md, "plain"))

    try:
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"[notify] Digest emailed to {recipient}")
        return True
    except Exception as e:
        print(f"[notify] Email failed: {e}")
        return False