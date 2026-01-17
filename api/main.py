# api/main.py FastAPI app entry point

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from settings import get_settings, setup_logging
import time

from api.routers import users, savings_accounts, debit_cards, credit_cards, expenses

settings = get_settings()
logger = setup_logging("api", "api.log")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    logger.info("=== Application Starting ===")
    logger.info(f"Environment: {settings.log_level}")
    
    yield  # Application runs while "yield" is active
    
    # Shutdown code here  
    logger.info("=== Application Shutting Down ===")

app = FastAPI(
    title="Expense Tracker API",
    description="A comprehensive expense tracking system with support for multiple payment methods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}", exc_info=True)
        raise
    
# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    
# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(savings_accounts.router, prefix="/api/v1")
app.include_router(debit_cards.router, prefix="/api/v1")
app.include_router(credit_cards.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")

@app.get("/", tags=["root"])
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Expense Tracker API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy"}