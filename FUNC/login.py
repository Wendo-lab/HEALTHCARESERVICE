# login.py
import requests
from fastapi import HTTPException
import httpx
import schemas
from sqlalchemy.orm import Session
from urllib.parse import quote_plus

def authenticate_user(db: Session, username: str, password: str):
    username = quote_plus(username)
    password = quote_plus(password)

    url = f"https://ussd.minet.co.ke/api/login.php?username={username}&password={password}"
    response = httpx.get(url)

    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == 0 and data.get("message") == "Success":
            user_data = data.get("data", [{}])[0]
            return {
                "message": "Login successful",
                "username": user_data.get("username"),
                "email": user_data.get("Email"),
                "full_name": user_data.get("Names"),
                "access_level": user_data.get("access"),
                "department": user_data.get("Department")
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid username or password")
    
    else:
        raise HTTPException(status_code=400, detail="Error in authentication with external service")
