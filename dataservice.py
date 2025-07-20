from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

# Initialize FastAPI app
app = FastAPI(
    title="Data Service API",
    description="A simple API for data operations",
    version="1.0.0"
)

# Response model for consistent API responses
class DataSearchResponse(BaseModel):
    message: str
    status: str

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Data Service API is running"}

@app.get("/datasearch", response_model=DataSearchResponse)
def datasearch():
    """
    Simple data search endpoint that returns a hello world message
    """
    return DataSearchResponse(
        message="Hello World from Data Search!",
        status="success"
    )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dataservice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
