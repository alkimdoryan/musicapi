from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import FXCommitJob
from app.services.commit_processor import process_commit_job
import json

router = APIRouter(
    prefix="/commit",
    tags=["FX Commit System"]
)

@router.post("/process")
async def commit_fx(
    file: UploadFile = File(...),
    job_json: str = Form(..., description="JSON string matching FXCommitJob schema")
):
    """
    Applies an effect with precise Time-Based Automation (Curve).
    This supports the 'FX Commit System' spec.
    
    - **file**: Input audio file (WAV/MP3)
    - **job_json**: JSON object defining FX, Static Params, and Automation Curve.
    """
    try:
        # Parse JSON
        job_data = json.loads(job_json)
        job = FXCommitJob(**job_data)
        
        # Read file
        audio_content = await file.read()
        
        # Process
        result_buffer = process_commit_job(audio_content, job)
        
        return StreamingResponse(
            result_buffer, 
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=committed_{job.fx}.wav"}
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in job_json")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Commit processing failed: {str(e)}")
