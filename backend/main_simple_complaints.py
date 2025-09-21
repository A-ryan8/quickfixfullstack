# Simple FastAPI server for complaint uploads
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json
import os
import requests
from datetime import datetime
from contextlib import asynccontextmanager
from database import get_db_connection, close_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up...")
    # Initialize database connection pool
    from database import initialize_pool
    if initialize_pool():
        print("Database connection pool initialized successfully")
    else:
        print("Database connection pool initialization failed")
    yield
    print("Server shutting down...")
    # Connection pool will be automatically cleaned up

app = FastAPI(title="Civic Engagement API", version="1.0.0", lifespan=lifespan)

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

# Database will be used instead of in-memory storage

class Complaint(BaseModel):
    id: int
    title: Optional[str] = None
    description: str
    location: str
    imageUrl: Optional[str] = None
    pdfUrl: Optional[str] = None
    status: str = "New"
    created_at: str
    
    class Config:
        # Allow datetime objects to be converted to strings
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ComplaintStats(BaseModel):
    total_complaints: int
    active_complaints: int
    resolved_today: int

@app.get("/")
def read_root():
    return {"message": "Civic Engagement API is running!"}

@app.get("/api/test-files")
def test_file_serving():
    """Test endpoint to check if files are being served correctly"""
    return {
        "message": "File serving test",
        "uploads_dir": "uploads/",
        "pdfs_dir": "pdfs/",
        "test_image_url": "http://localhost:8000/uploads/test.jpg",
        "test_pdf_url": "http://localhost:8000/pdfs/test.pdf"
    }

@app.get("/api/test-db")
def test_db_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn and conn.is_connected():
        return {"status": "ok", "message": "Successfully connected to the database."}
    else:
        return {"status": "error", "message": "Failed to connect to the database."}

@app.get("/api/complaints", response_model=list[Complaint])
def get_all_complaints():
    """Get all complaints from database"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")
        complaints = cursor.fetchall()
        
        # Convert all datetime objects to strings for Pydantic validation
        for complaint in complaints:
            for key, value in complaint.items():
                if isinstance(value, datetime):
                    complaint[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    complaint[key] = value.isoformat()
        
        return complaints
    except Exception as e:
        print(f"!!! DATABASE ERROR in get_all_complaints: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch complaints: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.get("/api/complaints/stats", response_model=ComplaintStats)
def get_complaint_stats():
    """Get complaint statistics from database"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    try:
        # Calculate total complaints
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_complaints = cursor.fetchone()[0]
        
        # Calculate active complaints (New or In Progress)
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('New', 'In Progress')")
        active_complaints = cursor.fetchone()[0]
        
        # Calculate resolved today (complaints that were updated to Resolved today)
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved' AND DATE(updated_at) = %s", (today,))
        resolved_today = cursor.fetchone()[0]
        
        return ComplaintStats(
            total_complaints=total_complaints,
            active_complaints=active_complaints,
            resolved_today=resolved_today
        )
        
    except Exception as e:
        print(f"!!! DATABASE ERROR in stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.post("/api/complaints/generate-ai")
def generate_ai_content(
    image_url: str = Form(...),
    location_context: str = Form(...)
):
    """Generate AI title and description for a complaint"""
    try:
        # Enhanced prompt for AI generation
        prompt = f"""
        Analyze this civic complaint image and location context: {location_context}
        
        Return a JSON response with exactly this structure:
        {{
            "title": "A short 3-5 word summary of the main issue",
            "description": "A detailed paragraph describing the problem, its impact, and suggested resolution"
        }}
        
        Examples:
        - For potholes: {{"title": "Road Pothole Issue", "description": "A significant pothole has developed on the road surface, creating a safety hazard for vehicles and pedestrians. The depression appears to be approximately 6 inches deep and 2 feet wide, with visible damage to the surrounding asphalt. This issue requires immediate attention to prevent vehicle damage and ensure safe passage for all road users."}}
        - For streetlights: {{"title": "Broken Street Light", "description": "A street light is not functioning properly, creating a dark area that poses safety risks for pedestrians and drivers during nighttime hours. The light appears to be completely out or flickering intermittently. This lighting issue should be addressed to maintain proper visibility and security in the area."}}
        
        Focus on municipal infrastructure issues and provide actionable descriptions.
        """
        
        # For now, return a mock response since we don't have actual AI integration
        # In production, this would call your AI service (Gemini, OpenAI, etc.)
        mock_response = {
            "title": "Municipal Infrastructure Issue",
            "description": f"A municipal infrastructure problem has been reported at {location_context}. The issue requires attention from the appropriate department to ensure public safety and proper maintenance of city services. Please review the attached image for detailed visual evidence of the problem."
        }
        
        return mock_response
        
    except Exception as e:
        print(f"Error generating AI content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI content: {e}")

@app.post("/api/complaints", response_model=Complaint)
def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None),
    pdf: UploadFile = File(None)
):
    """Create a new complaint with optional image and PDF upload"""
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
            print(f"Image uploaded successfully: {image_url}")
        except Exception as e:
            print(f"Error uploading image: {e}")
            # Continue without image if upload fails
    
    # Handle PDF upload if provided
    pdf_url = None
    if pdf and pdf.filename:
        try:
            # Create pdfs directory if it doesn't exist
            pdf_dir = "pdfs"
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(pdf.filename)[1]
            filename = f"complaint_{timestamp}{file_extension}"
            file_path = os.path.join(pdf_dir, filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = pdf.file.read()
                buffer.write(content)
            
            pdf_url = f"/pdfs/{filename}"
            print(f"PDF uploaded successfully: {pdf_url}")
        except Exception as e:
            print(f"Error uploading PDF: {e}")
            # Continue without PDF if upload fails
    
    # Insert into database
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    try:
        print("Attempting to insert record into database...")
        sql = "INSERT INTO complaints (title, description, location, imageUrl, pdfUrl, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (title, description, location, image_url, pdf_url, "New", datetime.now())
        cursor.execute(sql, values)
        
        print("Attempting to commit transaction...")
        db_conn.commit()
        
        new_complaint_id = cursor.lastrowid
        
        # Create response object
        new_complaint = Complaint(
            id=new_complaint_id,
            title=title,
            description=description,
            location=location,
            imageUrl=image_url,
            pdfUrl=pdf_url,
            status="New",
            created_at=datetime.now().isoformat()
        )
        
        return new_complaint
        
    except Exception as e:
        print(f"!!! DATABASE ERROR OCCURRED: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create complaint: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.put("/api/complaints/{complaint_id}")
def update_complaint_status(complaint_id: int, status_update: dict):
    """Update a complaint's status"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    try:
        # Check if complaint exists
        cursor.execute("SELECT id FROM complaints WHERE id = %s", (complaint_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Update the status
        new_status = status_update.get('status')
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        cursor.execute(
            "UPDATE complaints SET status = %s, updated_at = %s WHERE id = %s", 
            (new_status, datetime.now(), complaint_id)
        )
        db_conn.commit()
        
        return {"message": "Complaint status updated successfully", "id": complaint_id, "status": new_status}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"!!! DATABASE ERROR in update_complaint_status: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update complaint status: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(complaint_id: int):
    """Delete a complaint and its associated files"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    try:
        # First, get the complaint details to retrieve file paths
        cursor.execute("SELECT imageUrl, pdfUrl FROM complaints WHERE id = %s", (complaint_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        image_url, pdf_url = result
        
        # Delete the complaint from database
        cursor.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        db_conn.commit()
        
        # Delete associated files from filesystem
        files_deleted = []
        
        # Delete image file
        if image_url:
            try:
                # Remove leading slash if present
                image_path = image_url.lstrip('/')
                if os.path.exists(image_path):
                    os.remove(image_path)
                    files_deleted.append(f"Image: {image_path}")
                    print(f"Deleted image file: {image_path}")
            except Exception as e:
                print(f"Warning: Could not delete image file {image_url}: {e}")
        
        # Delete PDF file
        if pdf_url:
            try:
                # Remove leading slash if present
                pdf_path = pdf_url.lstrip('/')
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    files_deleted.append(f"PDF: {pdf_path}")
                    print(f"Deleted PDF file: {pdf_path}")
            except Exception as e:
                print(f"Warning: Could not delete PDF file {pdf_url}: {e}")
        
        return {
            "message": "Complaint deleted successfully",
            "id": complaint_id,
            "files_deleted": files_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"!!! DATABASE ERROR in delete_complaint: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete complaint: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

# Mount static files for serving uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
