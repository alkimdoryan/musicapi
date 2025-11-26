from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import AnalysisResponse
from app.services import file_io, analysis
from app.config import UPLOAD_DIR
import shutil
import os
from pathlib import Path

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio_endpoint(file: UploadFile = File(...)):
    """
    Upload an audio file and extract features (BPM, Key, Loudness, etc.) using Essentia.
    """
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    await file_io.save_upload_file(file, file_path)
    
    try:
        # Run analysis (synchronous for now as Essentia releases GIL often, but could be threaded)
        # For heavy load, this should be offloaded to a worker/thread pool.
        features = analysis.analyze_audio(str(file_path))
        
        return AnalysisResponse(
            filename=file.filename,
            bpm=features.get("bpm"),
            key=features.get("key"),
            scale=features.get("scale"),
            loudness=features.get("loudness"),
            danceability=features.get("danceability"),
            dynamic_complexity=features.get("dynamic_complexity")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
