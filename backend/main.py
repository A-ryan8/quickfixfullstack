from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import uvicorn
from database import get_db
from models import Complaint, ComplaintCreate, ComplaintUpdate, ComplaintStats
from prioritization_service import PrioritizationService
import security

# Load environment variables
load_dotenv()

app = FastAPI(title="Civic Complaint Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prioritization service
prioritization_service = PrioritizationService()

@app.get("/")
async def root():
    return {"message": "Civic Complaint Management API"}

@app.get("/api/complaints", response_model=List[Complaint])
async def get_all_complaints(db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_admin_user)):
    """Get all complaints (Admin only)"""
    complaints = db.query(Complaint).all()
    return complaints

@app.get("/api/complaints/public", response_model=List[Complaint])
async def get_public_complaints(db: Session = Depends(get_db)):
    """Get all complaints (Public access)"""
    complaints = db.query(Complaint).order_by(Complaint.priority_score.desc(), Complaint.created_at.desc()).all()
    return complaints

@app.post("/api/complaints", response_model=Complaint)
async def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_user)):
    """Create a new complaint (Authenticated users)"""
    db_complaint = Complaint(**complaint.dict())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    # Recalculate priorities after new complaint
    prioritization_service.recalculate_all_priorities(db)
    
    return db_complaint

@app.post("/api/complaints/submit", response_model=Complaint)
async def create_complaint_public(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None),
    pdf: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Create a new complaint (Public access)"""
    try:
        # Handle image upload
        image_url = None
        if image and image.filename:
            # Save image to uploads folder
            image_path = f"uploads/{image.filename}"
            os.makedirs("uploads", exist_ok=True)
            with open(image_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            image_url = f"/uploads/{image.filename}"
        
        # Handle PDF upload
        pdf_url = None
        if pdf and pdf.filename:
            # Save PDF to uploads folder
            pdf_path = f"uploads/{pdf.filename}"
            os.makedirs("uploads", exist_ok=True)
            with open(pdf_path, "wb") as buffer:
                content = await pdf.read()
                buffer.write(content)
            pdf_url = f"/uploads/{pdf.filename}"
        
        # Create complaint
        db_complaint = Complaint(
            title=title,
            description=description,
            location=location,
            image_url=image_url,
            pdf_url=pdf_url,
            status="pending",
            priority_score=0.0
        )
        
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        # Recalculate priorities after new complaint
        prioritization_service.recalculate_all_priorities(db)
        
        return db_complaint
        
    except Exception as e:
        print(f"Error creating complaint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create complaint: {e}")

@app.get("/api/complaints/stats", response_model=ComplaintStats)
async def get_complaint_stats(db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_admin_user)):
    """Get complaint statistics (Admin only)"""
    total_complaints = db.query(Complaint).count()
    pending_complaints = db.query(Complaint).filter(Complaint.status == "pending").count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == "resolved").count()
    
    # Calculate resolved today
    today = datetime.now().date()
    resolved_today = db.query(Complaint).filter(
        Complaint.status == "resolved",
        Complaint.updated_at >= today
    ).count()
    
    return ComplaintStats(
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        resolved_today=resolved_today
    )

@app.get("/api/complaints/stats/public", response_model=ComplaintStats)
async def get_public_complaint_stats(db: Session = Depends(get_db)):
    """Get complaint statistics (Public access)"""
    total_complaints = db.query(Complaint).count()
    pending_complaints = db.query(Complaint).filter(Complaint.status == "pending").count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == "resolved").count()
    
    # Calculate resolved today
    today = datetime.now().date()
    resolved_today = db.query(Complaint).filter(
        Complaint.status == "resolved",
        Complaint.updated_at >= today
    ).count()
    
    return ComplaintStats(
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        resolved_today=resolved_today
    )

@app.post("/api/complaints/recalculate-priorities")
async def recalculate_priorities(db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_admin_user)):
    """Recalculate all complaint priorities (Admin only)"""
    try:
        prioritization_service.recalculate_all_priorities(db)
        return {"message": "Priorities recalculated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recalculate priorities: {e}")

@app.put("/api/complaints/{complaint_id}")
async def update_complaint_status(
    complaint_id: int, 
    status: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """Update complaint status (Admin only)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = status
    complaint.updated_at = datetime.now()
    db.commit()
    
    # Recalculate priorities after status update
    prioritization_service.recalculate_all_priorities(db)
    
    return {"message": "Complaint status updated successfully"}

@app.delete("/api/complaints/{complaint_id}")
async def delete_complaint(complaint_id: int, db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_admin_user)):
    """Delete a complaint (Admin only)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    db.delete(complaint)
    db.commit()
    
    return {"message": "Complaint deleted successfully"}

@app.post("/api/complaints/{complaint_id}/upvote")
async def upvote_complaint(
    complaint_id: int,
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upvote a complaint (Public access)"""
    try:
        # Check if complaint exists
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Check if user already upvoted
        existing_upvote = db.execute(
            "SELECT id FROM upvotes WHERE complaint_id = :complaint_id AND user_id = :user_id",
            {"complaint_id": complaint_id, "user_id": user_id}
        ).fetchone()
        
        if existing_upvote:
            raise HTTPException(status_code=409, detail="User has already upvoted this complaint")
        
        # Add upvote
        db.execute(
            "INSERT INTO upvotes (complaint_id, user_id, created_at) VALUES (:complaint_id, :user_id, :created_at)",
            {"complaint_id": complaint_id, "user_id": user_id, "created_at": datetime.now()}
        )
        
        # Update upvote count
        db.execute(
            "UPDATE complaints SET upvote_count = upvote_count + 1 WHERE id = :complaint_id",
            {"complaint_id": complaint_id}
        )
        
        db.commit()
        
        # Recalculate priorities after upvote
        prioritization_service.recalculate_all_priorities(db)
        
        return {"message": "Complaint upvoted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error upvoting complaint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upvote complaint: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

