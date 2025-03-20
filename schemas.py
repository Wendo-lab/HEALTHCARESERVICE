from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from typing import List
from typing import Literal
from pydantic import EmailStr
from fastapi import Form
from typing import Union
from datetime import datetime
from fastapi import HTTPException


class ResponseSchema(BaseModel):
    question_id: int
    response: Optional[Union[bool, str]] = None  # Accepts boolean or string responses
    response_date: Optional[str] = None  # Expected in YYYY-MM-DD format
    reason: Optional[str] = None  # Stores explanations for non-binary responses
    file_path: Optional[str] = None  # Path to uploaded file

    @validator("response", pre=True)
    def validate_response(cls, value):
        if isinstance(value, str):
            # Check if value is a date (YYYY-MM-DD format)
            try:
                datetime.strptime(value, "%Y-%m-%d")  # Validates the format
                return None  # Move this value to response_date instead
            except ValueError:
                pass  # Continue checking other conditions

            lower_value = value.lower()
            if lower_value == "yes":
                return True
            elif lower_value == "no":
                return False
            elif lower_value.strip():  # Store other text responses
                return value

        return value  # Keep as is if already boolean or None

    @validator("response_date", pre=True)
    def validate_date_format(cls, value):
        if value:
            if isinstance(value, datetime):  # Convert datetime object to string
                return value.strftime("%Y-%m-%d")
            try:
                datetime.strptime(value, "%Y-%m-%d")  # Ensure valid date format
            except ValueError:
                raise ValueError("Date format must be YYYY-MM-DD")
        return value
    
    
class ClientResponseSchema(BaseModel):
    client_id: int
    question_id: int
    selected_months: List[str]  # List of month strings

    class Config:
        orm_mode = True

class ClientCreateSchema(BaseModel):
    client_name: str
    relationship_manager: str
    co_handler: str
    policy_period: str
    premium: str
    admin_fee: str
    income: str
    cover_type: Literal["Insured", "Hybrid", "Funded"]
    non_government: bool = False
    government: bool = False
    client_main_contact: str
    client_designation: str
    client_cell: str
    client_email: EmailStr

class ClientDetailsResponse(BaseModel):
    id: int
    relationship_manager: str
    co_handler: str
    policy_period: str
    premium: str
    admin_fee: str
    income: str
    cover_type: Literal["Insured", "Hybrid", "Funded"]
    non_government: bool
    government: bool
    client_main_contact: str
    client_designation: str
    client_cell: str
    client_email: EmailStr
    client_id: int

    class Config:
        orm_mode: True
    
class ExtraClientDetailsSchema(BaseModel):
    other_client_personel: Optional[str] = None
    designation: Optional[str] = None
    cell: Optional[str] = None
    email: Optional[EmailStr] = None
    client_id: int


class LoginRequestSchema(BaseModel):
    username: str
    password: str

class SignOutSchema(BaseModel):
    role: str
    confirmed_by: str  # Email of the person confirming
    status: str  # 'Pending' or 'Yes'
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

