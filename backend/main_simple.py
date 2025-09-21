# backend/main_simple.py - Simple version without database dependency
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Engagement API!"}

@app.get("/api/test")
def test_endpoint():
    return {"status": "ok", "message": "API is running correctly"}

@app.get("/api/test-db")
def test_db_connection():
    return {"status": "warning", "message": "Database connection not configured - using simple mode"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
