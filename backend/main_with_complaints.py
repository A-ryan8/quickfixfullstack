# backend/main_with_complaints.py - API with complaint upload endpoints
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Civic Engagement API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://10.30.243.189:8000",  # Your computer's IP
        "http://10.0.2.2:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ComplaintCreate(BaseModel):
    description: str
    location: str
    imageUrl: Optional[str] = None

class ComplaintUpdate(BaseModel):
    status: str

class Complaint(BaseModel):
    id: int
    description: str
    location: str
    imageUrl: Optional[str] = None
    status: str = "New"
    created_at: Optional[str] = None

# In-memory storage for demo (replace with database in production)
complaints_db = []
next_id = 1

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Engagement API!"}

@app.get("/api/test")
def test_endpoint():
    return {"status": "ok", "message": "API is running correctly"}

@app.get("/api/test-db")
def test_db_connection():
    return {"status": "ok", "message": "Using in-memory storage for demo"}

# --- COMPLAINT ENDPOINTS ---

@app.get("/api/complaints", response_model=list[Complaint])
def get_all_complaints():
    """Get all complaints"""
    return complaints_db

@app.post("/api/complaints", response_model=Complaint)
def create_complaint(
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None)
):
    """Create a new complaint with optional image upload"""
    global next_id
    
    # Handle image upload if provided
    image_url = None
    if image and image.filename:
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(image.filename)[1]
            filename = f"complaint_{timestamp}{file_extension}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = image.file.read()
                buffer.write(content)
            
            image_url = f"/uploads/{filename}"
        except Exception as e:
            print(f"Error uploading image: {e}")
            # Continue without image if upload fails
    
    new_complaint = Complaint(
        id=next_id,
        description=description,
        location=location,
        imageUrl=image_url,
        status="New",
        created_at=datetime.now().isoformat()
    )
    
    complaints_db.append(new_complaint)
    next_id += 1
    
    return new_complaint

@app.put("/api/complaints/{complaint_id}", response_model=Complaint)
def update_complaint_status(complaint_id: int, status_update: ComplaintUpdate):
    """Update complaint status"""
    for complaint in complaints_db:
        if complaint.id == complaint_id:
            complaint.status = status_update.status
            return complaint
    
    raise HTTPException(status_code=404, detail="Complaint not found")

@app.get("/api/complaints/{complaint_id}", response_model=Complaint)
def get_complaint(complaint_id: int):
    """Get a specific complaint by ID"""
    for complaint in complaints_db:
        if complaint.id == complaint_id:
            return complaint
    
    raise HTTPException(status_code=404, detail="Complaint not found")

@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(complaint_id: int):
    """Delete a complaint"""
    global complaints_db
    original_length = len(complaints_db)
    complaints_db = [c for c in complaints_db if c.id != complaint_id]
    
    if len(complaints_db) == original_length:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return {"message": "Complaint deleted successfully"}

# --- FILE UPLOAD ENDPOINT ---

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (image/video) for complaints"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return file info
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "file_path": file_path,
            "file_size": len(content),
            "content_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# --- BULK COMPLAINT CREATION ---

@app.post("/api/complaints/bulk", response_model=list[Complaint])
def create_multiple_complaints(complaints: list[ComplaintCreate]):
    """Create multiple complaints at once"""
    global next_id
    created_complaints = []
    
    for complaint_data in complaints:
        new_complaint = Complaint(
            id=next_id,
            description=complaint_data.description,
            location=complaint_data.location,
            imageUrl=complaint_data.imageUrl,
            status="New",
            created_at=datetime.now().isoformat()
        )
        complaints_db.append(new_complaint)
        created_complaints.append(new_complaint)
        next_id += 1
    
    return created_complaints

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
