"""
Upload Router - Handles large file uploads
Files are saved to disk and referenced by ID for subsequent processing.
This prevents browser crashes from loading large files into memory.
"""
import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import soundfile as sf
import numpy as np
import io

router = APIRouter(prefix="/upload", tags=["upload"])

# Base directory for uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Preview duration in seconds
PREVIEW_DURATION = 30


@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload a large audio file to the server.
    Returns a file_id that can be used for subsequent processing.
    """
    # Generate unique ID
    file_id = str(uuid.uuid4())
    
    # Get file extension
    original_name = file.filename or "audio.wav"
    ext = os.path.splitext(original_name)[1] or ".wav"
    
    # Save to disk
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get basic file info without loading entire file
        info = sf.info(file_path)
        
        return {
            "file_id": file_id,
            "original_name": original_name,
            "duration_seconds": info.duration,
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2)
        }
    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/stream/{file_id}")
async def stream_audio(file_id: str):
    """
    Stream the full uploaded audio file.
    Browser can load this progressively without crashing.
    """
    # Find the file (could be any extension)
    file_path = None
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(file_id):
            file_path = os.path.join(UPLOAD_DIR, f)
            break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file directly - browser handles streaming
    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=f"audio_{file_id}.wav"
    )


@router.get("/file/{file_id}")
async def get_file_path(file_id: str):
    """
    Get the server-side file path for backend processing.
    Other routers (commit, stems, etc.) can use this to process the full file.
    """
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(file_id):
            return {"file_path": os.path.join(UPLOAD_DIR, f)}
    
    raise HTTPException(status_code=404, detail="File not found")


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Delete an uploaded file when no longer needed.
    """
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(file_id):
            os.remove(os.path.join(UPLOAD_DIR, f))
            return {"deleted": True, "file_id": file_id}
    
    raise HTTPException(status_code=404, detail="File not found")
