# backend/main.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import get_db_connection, close_db_connection
from models import ComplaintCreate, Complaint, ComplaintUpdate
import os
import shutil
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up...")
    get_db_connection()
    yield
    print("Server shutting down...")
    close_db_connection()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads and PDFs
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
if os.path.exists("pdfs"):
    app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Engagement API!"}

@app.get("/api/test")
def test_endpoint():
    return {"status": "ok", "message": "API is running correctly"}

# --- NEW ENDPOINT TO CREATE A COMPLAINT ---
@app.post("/api/complaints")
async def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None),
    pdf: UploadFile = File(None)
):
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor()
    
    # Generate unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_url = None
    pdf_url = None
    
    try:
        # Save image file if provided
        if image and image.filename:
            image_extension = os.path.splitext(image.filename)[1]
            image_filename = f"complaint_{timestamp}{image_extension}"
            image_path = os.path.join("uploads", image_filename)
            
            # Ensure uploads directory exists
            os.makedirs("uploads", exist_ok=True)
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_url = f"uploads/{image_filename}"
        
        # Save PDF file if provided
        if pdf and pdf.filename:
            pdf_extension = os.path.splitext(pdf.filename)[1]
            pdf_filename = f"complaint_{timestamp}{pdf_extension}"
            pdf_path = os.path.join("pdfs", pdf_filename)
            
            # Ensure pdfs directory exists
            os.makedirs("pdfs", exist_ok=True)
            
            with open(pdf_path, "wb") as buffer:
                shutil.copyfileobj(pdf.file, buffer)
            pdf_url = f"pdfs/{pdf_filename}"
        
        # SQL query to insert a new complaint
        sql = "INSERT INTO complaints (title, description, location, imageUrl, pdfUrl) VALUES (%s, %s, %s, %s, %s)"
        values = (title, description, location, image_url, pdf_url)
        
        print("Attempting to insert record into database...")
        cursor.execute(sql, values)
        print("Attempting to commit transaction...")
        db_conn.commit() # Commit the transaction to save the data
        
        new_complaint_id = cursor.lastrowid # Get the ID of the new row
        
        # Create a full complaint object to return
        created_complaint = Complaint(
            id=new_complaint_id,
            title=title,
            description=description,
            location=location,
            imageUrl=image_url or "",
            status="New" # Default status
        )
        return created_complaint
        
    except Exception as e:
        print(f"!!! DATABASE ERROR OCCURRED: {e}")
        db_conn.rollback() # Rollback in case of error
        
        # Clean up uploaded files if database operation failed
        if image_url and os.path.exists(image_url):
            os.remove(image_url)
        if pdf_url and os.path.exists(pdf_url):
            os.remove(pdf_url)
            
        raise HTTPException(status_code=500, detail=f"Failed to create complaint: {e}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

# --- NEW ENDPOINT TO UPDATE A COMPLAINT'S STATUS ---
@app.put("/api/complaints/{complaint_id}", response_model=Complaint)
def update_complaint_status(complaint_id: int, status_update: ComplaintUpdate):
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        # First, check if the complaint exists
        cursor.execute("SELECT * FROM complaints WHERE id = %s", (complaint_id,))
        existing_complaint = cursor.fetchone()
        if not existing_complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # SQL query to update the status of a specific complaint
        update_sql = "UPDATE complaints SET status = %s WHERE id = %s"
        cursor.execute(update_sql, (status_update.status, complaint_id))
        
        # Verify that a row was actually updated
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")
            
        db_conn.commit()
        
        # Fetch the updated complaint to return it
        cursor.execute("SELECT * FROM complaints WHERE id = %s", (complaint_id,))
        updated_complaint = cursor.fetchone()
        
        return updated_complaint
        
    except Exception as e:
        db_conn.rollback()
        # Re-raise HTTPException if it's already one
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update complaint: {str(e)}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

# --- NEW ENDPOINT TO GET ALL COMPLAINTS ---
@app.get("/api/complaints")
def get_all_complaints():
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        # SQL query to get all complaints
        cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")
        complaints = cursor.fetchall()
        
        # Format the response to ensure all fields are properly handled
        formatted_complaints = []
        for complaint in complaints:
            formatted_complaint = {
                "id": complaint["id"],
                "title": complaint.get("title"),
                "description": complaint["description"],
                "location": complaint["location"],
                "imageUrl": complaint.get("imageUrl", ""),
                "status": complaint["status"],
                "created_at": complaint["created_at"].isoformat() if complaint.get("created_at") else None,
                "updated_at": complaint["updated_at"].isoformat() if complaint.get("updated_at") else None,
                "pdfUrl": complaint.get("pdfUrl")
            }
            formatted_complaints.append(formatted_complaint)
        
        return formatted_complaints
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch complaints: {str(e)}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.get("/api/complaints/stats")
def get_complaints_stats():
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        # Get total complaints count
        cursor.execute("SELECT COUNT(*) as total FROM complaints")
        total_result = cursor.fetchone()
        total_complaints = total_result['total'] if total_result else 0
        
        # Get complaints by status
        cursor.execute("SELECT status, COUNT(*) as count FROM complaints GROUP BY status")
        status_results = cursor.fetchall()
        status_counts = {row['status']: row['count'] for row in status_results}
        
        # Get recent complaints (last 7 days)
        cursor.execute("SELECT COUNT(*) as recent FROM complaints WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAYS)")
        recent_result = cursor.fetchone()
        recent_complaints = recent_result['recent'] if recent_result else 0
        
        # Get complaints by month (last 6 months)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(created_at, '%%Y-%%m') as month,
                COUNT(*) as count 
            FROM complaints 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
            ORDER BY month DESC
        """)
        monthly_results = cursor.fetchall()
        monthly_counts = {row['month']: row['count'] for row in monthly_results}
        
        return {
            "total_complaints": total_complaints,
            "recent_complaints": recent_complaints,
            "status_counts": status_counts,
            "monthly_counts": monthly_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(complaint_id: int):
    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = db_conn.cursor(dictionary=True)
    
    try:
        # First, get the complaint details to retrieve file paths
        cursor.execute("SELECT imageUrl, pdfUrl FROM complaints WHERE id = %s", (complaint_id,))
        complaint = cursor.fetchone()
        
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Delete the complaint from database
        cursor.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        db_conn.commit()
        
        # Delete associated files
        try:
            # Delete image file if it exists
            if complaint.get('imageUrl'):
                image_path = complaint['imageUrl']
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
            
            # Delete PDF file if it exists
            if complaint.get('pdfUrl'):
                pdf_path = complaint['pdfUrl']
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"Deleted PDF file: {pdf_path}")
        except Exception as file_error:
            print(f"Warning: Could not delete some files: {file_error}")
            # Don't fail the request if file deletion fails
        
        return {"message": "Complaint deleted successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete complaint: {str(e)}")
    finally:
        cursor.close()
        close_db_connection(db_conn)

@app.get("/api/test-db")
def test_db_connection():
    conn = get_db_connection()
    if conn and conn.is_connected():
        return {"status": "ok", "message": "Successfully connected to the database."}
    else:
        return {"status": "error", "message": "Failed to connect to the database."}
