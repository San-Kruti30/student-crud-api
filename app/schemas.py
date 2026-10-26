from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+?[0-9\- ]{7,15}$"

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def check_rules(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email or a phone number")
        if self.date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return self

class StudentUpdate(BaseModel):      # every field optional, for updates
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

class StudentOut(StudentBase):
    id: int