"""
Carbon Footprint Tracker - FastAPI Backend
Main application entry point
"""

import os
import database
import routes
from database import init_db
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

init_db()

app = FastAPI(
    title="Carbon Footprint Tracker API",
    description="Track and reduce your carbon footprint with personalized insights",
    version="1.0.0"
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.get("/")
def read_root():
    return {
        "name": "Carbon Footprint Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.on_event("startup")
async def startup_event():
    print("🌍 Carbon Footprint Tracker API started")
    print("📊 Database initialized")
    print(f"🔒 CORS Origins: {ALLOWED_ORIGINS}")
    print("🚀 Ready to track carbon emissions!")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Carbon Footprint Tracker API shutting down")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "development") == "development"
    )