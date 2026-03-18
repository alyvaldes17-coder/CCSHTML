from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from database import create_db_and_tables
from features.auth import routes as auth_routes
from routes import admin, stripe, nike

# Load env
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Nike Bot Pro - Auth Server",
    version="1.0.0",
    description="Authentication & payment processing for Nike Bot Pro SaaS",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create DB tables
@app.on_event("startup")
async def startup():
    create_db_and_tables()

# Configure CORS (Tauri desktop + web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-HWID"],  # Important: X-HWID custom header
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(admin.router)
app.include_router(stripe.router)
app.include_router(nike.router)

@app.get("/")
async def root():
    return {
        "message": "Nike Bot Pro - Auth Server",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        reload=True
    )
