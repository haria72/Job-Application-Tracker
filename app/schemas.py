from pydantic import BaseModel
from typing import Optional
from datetime import date

class ApplicationCreate(BaseModel):
    company: str
    role: str
    link: Optional[str] = None
    platform: str
    app_type: str
    stage: Optional[str] = "applied"
    applied_date: date
    response_date: Optional[date] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    link: Optional[str] = None
    stage: Optional[str] = None
    response_date: Optional[date] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    company: str
    role: str
    link: Optional[str] = None
    platform: str
    app_type: str
    stage: str
    applied_date: date
    response_date: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True #for pydantic to read data from SQLAlchemy model instances and convert them to Pydantic models when returning responses instead of expecting a dict