# backend/models.py
from pydantic import BaseModel, Field
from typing import Optional

class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    location: str
    imageUrl: str

class Complaint(BaseModel):
    id: int
    title: Optional[str] = None
    description: str
    location: str
    imageUrl: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pdfUrl: Optional[str] = None

class ComplaintUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)
