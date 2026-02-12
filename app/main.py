from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

# 1. Configure Professional Logging
# This sets up the format: [TIME] [LEVEL] [MESSAGE]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import your router
from app.api.endpoints import router as analysis_router

app = FastAPI(title="AIONYX API", version="2.0")

# 2. CORS (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. OBSERVABILITY LAYER (Middleware)
# This function runs for EVERY request to time it.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Log the incoming request
    logger.info(f"➡️ Incoming Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate duration
    process_time = time.time() - start_time
    
    # Log the completion
    logger.info(f"✅ Completed in {process_time:.4f} seconds | Status: {response.status_code}")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include your routes
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "AIONYX System Operational", "version": "2.0"}