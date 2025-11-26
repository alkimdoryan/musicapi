import time
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models import StemResponse
from app.config import UPLOAD_DIR
from app.services import file_io, demucs

router = APIRouter(prefix="/stems", tags=["stems"])

@router.post("/extract", response_model=StemResponse)
async def extract_stems(
    audio_file: UploadFile = File(...),
    separation_model: str = Form("ht_demucs", description="Model to use: ht_demucs"),
):
    start_time = time.time()
    
    # Validate model name
    valid_models = ["ht_demucs"]
    if separation_model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model name. Only {valid_models} is supported.")

    # Save uploaded file
    file_path = UPLOAD_DIR / audio_file.filename
    await file_io.save_upload_file(audio_file, file_path)
    
    try:
        # Dispatch to appropriate service
        if separation_model == "ht_demucs":
            stems = await demucs.run_model(str(file_path), separation_model)
        else:
            raise HTTPException(status_code=400, detail="Model not implemented")
            
        processing_time = time.time() - start_time
        
        return StemResponse(
            status="ok",
            model=separation_model,
            stems=stems,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Optional: Clean up uploaded file
        # if file_path.exists():
        #     file_path.unlink()
        pass
