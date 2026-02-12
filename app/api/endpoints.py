from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
import io
import logging
from typing import Dict, Any

# Import services
from app.services.profiler import analyze_dataset
from app.services.ai_analyst import generate_data_story, ask_data_question
from app.services.validator import validate_analysis_intent
from app.schemas.profile import ProfileReport

# Initialize Logger
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Request Models ---
class ChatRequest(BaseModel):
    question: str
    profile: Dict[str, Any]

class AnalysisPlanRequest(BaseModel):
    question: str
    profile: Dict[str, Any]

# --- 1. Analysis Endpoint ---
@router.post("/analyze", response_model=ProfileReport)
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        logger.warning(f"❌ Rejected file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    logger.info(f"📂 Processing file: {file.filename}")

    try:
        # Read file
        contents = await file.read()
        buffer = io.BytesIO(contents)
        df = pd.read_csv(buffer)
        
        # Profile
        logger.info(f"📊 Profiling dataframe with {df.shape[0]} rows.")
        report = analyze_dataset(df, file.filename)

        # AI Analysis
        logger.info("🤖 Sending profile to Gemini AI...")
        report_dict = report.model_dump()
        ai_text = generate_data_story(report_dict)
        report.ai_analysis = ai_text
        
        logger.info("✅ Analysis complete.")
        return report

    except Exception as e:
        logger.error(f"🔥 Analysis CRASHED: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# --- 2. Chat Endpoint ---
@router.post("/chat")
async def chat_with_data(request: ChatRequest):
    logger.info(f"💬 Chat Question: '{request.question}'")
    try:
        answer = ask_data_question(request.profile, request.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# --- 3. Planning Endpoint ---
@router.post("/analysis/plan")
async def plan_analysis(request: AnalysisPlanRequest):
    logger.info(f"🛡️ Validating Intent: '{request.question}'")
    try:
        validation = validate_analysis_intent(request.profile, request.question)
        if not validation["is_valid"]:
            logger.warning(f"🚫 Blocked Invalid Intent: {validation['warning']}")
        return validation
    except Exception as e:
        logger.error(f"Planning Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")