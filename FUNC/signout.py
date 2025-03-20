from sqlalchemy.orm import Session
from models import SignOut
from schemas import SignOutSchema
from datetime import datetime
from FUNC.email import send_email  
from FUNC.role_hierachy import get_users_by_role, get_next_role_users  
from fastapi import HTTPException
import jwt  # For generating secure confirmation links

SECRET_KEY = "your_secret_key"

def generate_confirmation_link(role: str, email: str):
    """Generate a secure confirmation link for email approval."""
    token = jwt.encode({"role": role, "confirmed_by": email}, SECRET_KEY, algorithm="HS256")
    return f"http://127.0.0.1:8000/signoffs/confirm-email/?token={token}"

def confirm_sign_off(db: Session, role: str, confirmed_by: str):
    """Handles sign-off and moves to the next role once confirmed."""

    valid_users = get_users_by_role(role)

    # Debugging prints
    print(f"Decoded Role: {role}")
    print(f"Decoded Confirmed By: {confirmed_by}")
    print(f"Valid Users for Role: {valid_users}")

    if confirmed_by not in valid_users:
        raise HTTPException(status_code=403, detail="Unauthorized: Email not allowed to confirm for this role.")

    # Insert new confirmation record without checking existing ones
    sign_off = SignOut(
        role=role,
        status="Yes",
        confirmed_by=confirmed_by,
        timestamp=datetime.utcnow()
    )
    db.add(sign_off)
    db.commit()
    db.refresh(sign_off)

    # Move to the next role subject to change
    next_users = get_next_role_users(role)
    if next_users:
        confirmation_links = [generate_confirmation_link(role, email) for email in next_users]
        subject = f"Sign-Off Required: {role} Confirmed"
        message = f"{role} confirmed by {confirmed_by}.\n\nClick the link below to confirm your sign-off:\n"
        message += "\n".join(confirmation_links)
        send_email(sender=confirmed_by, recipients=next_users, subject=subject, message=message)

    return sign_off
