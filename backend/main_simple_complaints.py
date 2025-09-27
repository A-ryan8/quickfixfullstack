# Simple FastAPI server for complaint uploads
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends
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
from prioritization_service import update_all_priority_scores, _calculate_priority_score
import security

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
    priority_score: Optional[float] = None
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
def get_all_complaints(current_user: dict = Depends(security.get_current_admin_user)):
    """Get all complaints from database (Admin only)"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                id, title, description, location, status, 
                image_url as imageUrl, pdf_url as pdfUrl, created_at, updated_at,
                COALESCE(upvote_count, 0) as upvote_count,
                COALESCE(priority_score, 0) as priority_score
            FROM complaints 
            ORDER BY priority_score DESC, created_at DESC
        """)
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

@app.get("/api/complaints/public", response_model=list[Complaint])
def get_public_complaints():
    """Get all complaints for public viewing (no authentication required)"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                id, title, description, location, status, 
                image_url as imageUrl, pdf_url as pdfUrl, created_at, updated_at,
                COALESCE(upvote_count, 0) as upvote_count,
                COALESCE(priority_score, 0) as priority_score
            FROM complaints 
            ORDER BY priority_score DESC, created_at DESC
        """)
        complaints = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for complaint in complaints:
            if complaint.get('created_at'):
                complaint['created_at'] = complaint['created_at'].isoformat()
            if complaint.get('updated_at'):
                complaint['updated_at'] = complaint['updated_at'].isoformat()
        
        return complaints
    except Exception as e:
        print(f"!!! DATABASE ERROR in get_public_complaints: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch complaints: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.get("/api/complaints/stats/public", response_model=ComplaintStats)
def get_public_complaint_stats():
    """Get complaint statistics (public endpoint - no authentication required)"""
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
        
        # Calculate resolved complaints
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        resolved_complaints = cursor.fetchone()[0]
        
        # Calculate high priority complaints (priority_score > 5.0)
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority_score > 5.0")
        high_priority_complaints = cursor.fetchone()[0]
        
        # Calculate resolved today (complaints resolved today)
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved' AND DATE(updated_at) = CURDATE()")
        resolved_today = cursor.fetchone()[0]
        
        return ComplaintStats(
            total_complaints=total_complaints,
            active_complaints=active_complaints,
            resolved_today=resolved_today
        )
    except Exception as e:
        print(f"!!! DATABASE ERROR in public stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)  # Return connection to pool

@app.get("/api/complaints/stats", response_model=ComplaintStats)
def get_complaint_stats(current_user: dict = Depends(security.get_current_admin_user)):
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

@app.post("/api/complaints/recalculate-priorities")
def recalculate_priorities(current_user: dict = Depends(security.get_current_admin_user)):
    """Recalculate priority scores for unresolved complaints and update DB."""
    try:
        result = update_all_priority_scores()
        return {"message": "Priority scores recalculated", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recalculate priorities: {e}")

@app.post("/api/complaints/generate-ai")
def generate_ai_content(
    current_user: dict = Depends(security.get_current_admin_user),
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

@app.post("/api/complaints/submit", response_model=Complaint)
async def create_complaint_public(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None),
    pdf: UploadFile = File(None)
):
    """Create a new complaint with optional image and PDF upload (public endpoint - no authentication required)"""
    
    # Handle image upload if provided
    image_url = None
    if image and image.filename:
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complaint_{timestamp}.{image.filename.split('.')[-1]}"
            file_path = os.path.join("uploads", filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            
            image_url = f"/uploads/{filename}"
            print(f"Image uploaded successfully: {image_url}")
        except Exception as e:
            print(f"Error uploading image: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")
    
    # Handle PDF upload if provided
    pdf_url = None
    if pdf and pdf.filename:
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complaint_{timestamp}.pdf"
            file_path = os.path.join("uploads", filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await pdf.read()
                buffer.write(content)
            
            pdf_url = f"/uploads/{filename}"
            print(f"PDF uploaded successfully: {pdf_url}")
        except Exception as e:
            print(f"Error uploading PDF: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {e}")
    
    # Use provided description
    ai_description = description
    
    # Save to database
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        # Insert complaint into database
        cursor.execute("""
            INSERT INTO complaints (title, description, location, image_url, pdf_url, status, created_at, ai_urgency, priority_score, upvote_count, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            title,
            ai_description,
            location,
            image_url,
            pdf_url,
            "New",
            datetime.now(),
            0.5,  # Default AI urgency
            0.0,  # Default priority score
            0,    # Default upvote count
            None  # No user_id for public submissions
        ))
        
        complaint_id = cursor.lastrowid
        
        # Calculate priority score
        try:
            priority_score, hours_old = _calculate_priority_score(0.5, 0, datetime.now().isoformat())
        except Exception as e:
            print(f"Error calculating priority score: {e}")
            priority_score = 0.5  # Default priority score
        
        # Update priority score
        cursor.execute("""
            UPDATE complaints 
            SET priority_score = %s 
            WHERE id = %s
        """, (priority_score, complaint_id))
        
        db_conn.commit()
        
        # Return the created complaint
        return Complaint(
            id=complaint_id,
            title=title,
            description=ai_description,
            location=location,
            imageUrl=image_url,
            status="New",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            pdfUrl=pdf_url,
            aiUrgency=0.5,
            priorityScore=priority_score,
            upvoteCount=0,
            userId=None
        )
        
    except Exception as e:
        db_conn.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create complaint: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.post("/api/complaints", response_model=Complaint)
def create_complaint(
    current_user: dict = Depends(security.get_current_user),
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
def update_complaint_status(complaint_id: int, status_update: dict, current_user: dict = Depends(security.get_current_admin_user_bypass)):
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
def delete_complaint(complaint_id: int, current_user: dict = Depends(security.get_current_admin_user_bypass)):
    """Delete a complaint and its associated files"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    try:
        # First, get the complaint details to retrieve file paths
        cursor.execute("SELECT image_url, pdf_url FROM complaints WHERE id = %s", (complaint_id,))
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

@app.post("/api/complaints/{complaint_id}/upvote")
async def upvote_complaint(complaint_id: int, request: Request):
    """
    Public upvote endpoint that allows anonymous upvoting.
    Uses IP address to prevent duplicate votes from the same source.
    """
    # Get client IP address for tracking
    client_ip = request.client.host
    user_id = f"anonymous_{client_ip}"

    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db_conn.cursor(dictionary=True)

    try:
        # First, check if the complaint exists
        cursor.execute("SELECT id FROM complaints WHERE id = %s", (complaint_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Check if upvotes table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upvotes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                complaint_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_complaint (user_id, complaint_id),
                FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_complaint_id (complaint_id)
            )
        """)
        
        # Ensure upvote_count column exists in complaints table
        cursor.execute("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 0")

        # Check if user has already upvoted this complaint
        cursor.execute(
            "SELECT id FROM upvotes WHERE user_id = %s AND complaint_id = %s", 
            (user_id, complaint_id)
        )
        existing_vote = cursor.fetchone()
        if existing_vote:
            raise HTTPException(status_code=409, detail="User has already upvoted this complaint")

        # Add the upvote record
        cursor.execute(
            "INSERT INTO upvotes (user_id, complaint_id) VALUES (%s, %s)",
            (user_id, complaint_id)
        )

        # Increment upvote count in complaints table
        cursor.execute(
            "UPDATE complaints SET upvote_count = COALESCE(upvote_count, 0) + 1 WHERE id = %s", 
            (complaint_id,)
        )

        # Recalculate priority score for this specific complaint
        cursor.execute(
            """
            SELECT 
                COALESCE(ai_urgency, 0) AS ai_urgency,
                COALESCE(upvote_count, 0) AS upvotes,
                created_at
            FROM complaints 
            WHERE id = %s
            """,
            (complaint_id,)
        )
        row = cursor.fetchone()
        if row:
            created_at = row.get("created_at")
            created_at_str = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or "")
            score, _ = _calculate_priority_score(float(row.get("ai_urgency") or 0.0), int(row.get("upvotes") or 0), created_at_str)
            cursor.execute("UPDATE complaints SET priority_score = %s WHERE id = %s", (score, complaint_id))

        db_conn.commit()

        return {
            "message": "Upvoted successfully", 
            "complaint_id": complaint_id,
            "user_id": user_id,
            "new_priority_score": score if 'score' in locals() else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"!!! DATABASE ERROR in upvote: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upvote: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.get("/api/debug/upvotes/{complaint_id}")
def debug_upvotes(complaint_id: int):
    """Debug endpoint to check upvote status for a complaint"""
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db_conn.cursor(dictionary=True)

    try:
        # Check if upvotes table exists
        cursor.execute("SHOW TABLES LIKE 'upvotes'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return {"error": "upvotes table does not exist"}

        # Get all upvotes for this complaint
        cursor.execute("SELECT * FROM upvotes WHERE complaint_id = %s", (complaint_id,))
        upvotes = cursor.fetchall()

        # Get complaint details
        cursor.execute("SELECT id, upvote_count, priority_score FROM complaints WHERE id = %s", (complaint_id,))
        complaint = cursor.fetchone()

        return {
            "complaint_id": complaint_id,
            "table_exists": True,
            "upvotes": upvotes,
            "complaint_details": complaint,
            "total_upvotes": len(upvotes)
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.post("/api/debug/request-info")
async def debug_request_info(request: Request):
    """Debug endpoint to see what the Flutter app is sending"""
    try:
        content_type = request.headers.get("content-type", "")
        print(f"DEBUG: Content-Type: {content_type}")
        
        if "application/json" in content_type:
            body = await request.json()
            return {
                "content_type": content_type,
                "body": body,
                "body_type": type(body).__name__
            }
        else:
            form_data = await request.form()
            return {
                "content_type": content_type,
                "form_data": dict(form_data),
                "form_data_type": type(form_data).__name__
            }
    except Exception as e:
        return {
            "error": str(e),
            "content_type": request.headers.get("content-type", ""),
            "headers": dict(request.headers)
        }

@app.post("/api/complaints/{complaint_id}/upvote/public")
async def upvote_complaint_public(complaint_id: int, request: Request):
    """
    Public upvote endpoint - no authentication required
    Uses Firebase user ID for proper user tracking
    """
    # Get user_id from request body
    try:
        body = await request.json()
        user_id = body.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db_conn.cursor(dictionary=True)

    try:
        # First, check if the complaint exists
        cursor.execute("SELECT id FROM complaints WHERE id = %s", (complaint_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Check if upvotes table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upvotes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                complaint_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_complaint (user_id, complaint_id),
                FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_complaint_id (complaint_id)
            )
        """)
        
        # Ensure upvote_count column exists in complaints table
        cursor.execute("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 0")

        # Check if user has already upvoted this complaint
        cursor.execute(
            "SELECT id FROM upvotes WHERE user_id = %s AND complaint_id = %s", 
            (user_id, complaint_id)
        )
        existing_vote = cursor.fetchone()
        if existing_vote:
            return {"message": "Already upvoted", "already_voted": True}

        # Add the upvote record
        cursor.execute(
            "INSERT INTO upvotes (user_id, complaint_id) VALUES (%s, %s)",
            (user_id, complaint_id)
        )

        # Increment upvote count in complaints table
        cursor.execute(
            "UPDATE complaints SET upvote_count = COALESCE(upvote_count, 0) + 1 WHERE id = %s", 
            (complaint_id,)
        )

        # Recalculate priority score for this specific complaint
        cursor.execute(
            """
            SELECT 
                COALESCE(ai_urgency, 0) AS ai_urgency,
                COALESCE(upvote_count, 0) AS upvotes,
                created_at
            FROM complaints 
            WHERE id = %s
            """,
            (complaint_id,)
        )
        row = cursor.fetchone()
        if row:
            created_at = row.get("created_at")
            created_at_str = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or "")
            score, _ = _calculate_priority_score(float(row.get("ai_urgency") or 0.0), int(row.get("upvotes") or 0), created_at_str)
            cursor.execute("UPDATE complaints SET priority_score = %s WHERE id = %s", (score, complaint_id))

        db_conn.commit()

        return {
            "message": "Upvoted successfully", 
            "complaint_id": complaint_id,
            "user_id": user_id,
            "new_priority_score": score if 'score' in locals() else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"!!! DATABASE ERROR in public upvote: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upvote: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.post("/api/test/upvote/{complaint_id}")
async def test_upvote(complaint_id: int):
    """Test upvote endpoint with hardcoded user_id for debugging"""
    user_id = "test_user_123"
    
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db_conn.cursor(dictionary=True)

    try:
        # First, check if the complaint exists
        cursor.execute("SELECT id FROM complaints WHERE id = %s", (complaint_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Check if upvotes table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upvotes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                complaint_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_complaint (user_id, complaint_id),
                FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_complaint_id (complaint_id)
            )
        """)
        
        # Ensure upvote_count column exists in complaints table
        cursor.execute("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 0")

        # Check if user has already upvoted this complaint
        cursor.execute(
            "SELECT id FROM upvotes WHERE user_id = %s AND complaint_id = %s", 
            (user_id, complaint_id)
        )
        existing_vote = cursor.fetchone()
        if existing_vote:
            return {"message": "User has already upvoted this complaint", "already_voted": True}

        # Add the upvote record
        cursor.execute(
            "INSERT INTO upvotes (user_id, complaint_id) VALUES (%s, %s)",
            (user_id, complaint_id)
        )

        # Increment upvote count in complaints table
        cursor.execute(
            "UPDATE complaints SET upvote_count = COALESCE(upvote_count, 0) + 1 WHERE id = %s", 
            (complaint_id,)
        )

        db_conn.commit()

        return {
            "message": "Test upvote successful", 
            "complaint_id": complaint_id,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"!!! DATABASE ERROR in test upvote: {e}")
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upvote: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

# Mount static files for serving uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
