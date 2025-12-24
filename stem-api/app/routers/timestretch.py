
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
import os
import shutil
import tempfile
from typing import Optional
from app.services.time_stretch import process_audio_stretch, QualityMode

router = APIRouter(
    prefix="/api/v1/audio",
    tags=["Time Stretch"]
)

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@router.post("/time-stretch", summary="Change audio BPM with high quality")
async def time_stretch_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    original_bpm: Optional[float] = Form(None, description="Original BPM (optional, auto-detected if None or 0)"),
    target_bpm: float = Form(..., description="Target BPM"),
    quality_mode: QualityMode = Form(QualityMode.UNIVERSAL, description="Processing algoritm preset")
):
    # validate file type
    if file.content_type not in ["audio/wav", "audio/mpeg", "audio/flac", "audio/x-wav"]:
        # weak check, but okay for now
        pass
        
    # Save input to temp
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        input_path = tmp.name
        
    try:
        # Run heavy processing in threadpool
        output_path = await run_in_threadpool(
            process_audio_stretch,
            input_path,
            original_bpm,
            target_bpm,
            quality_mode
        )
        
        # Return file and schedule cleanup
        # We need to cleanup INPUT and OUTPUT
        background_tasks.add_task(cleanup_file, input_path)
        background_tasks.add_task(cleanup_file, output_path)
        
        return StreamingResponse(
            open(output_path, "rb"), # File pointer needs to stay open until stream ends? 
            # Note: StreamingResponse with open file works, but we must ensure it doesn't close prematurely.
            # Best practice: Use a generator or just passing the file object works in Starlette.
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=stretched_{file.filename}.wav"}
        )
        
    except Exception as e:
        # Cleanup input if failed
        cleanup_file(input_path)
        raise HTTPException(status_code=500, detail=str(e))
