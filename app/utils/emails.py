from flask_mail import Message
from app import mail

def send_email(subject, recipient, body):
    """
    Sends an email to the recipient with the specified subject and body.
    """
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
