from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models import MasteringResponse
from app.services import file_io, mastering
from app.config import UPLOAD_DIR, OUTPUT_DIR
from typing import Optional, Union
from pathlib import Path

router = APIRouter(
    prefix="/mastering",
    tags=["mastering"],
    responses={404: {"description": "Not found"}},
)

@router.post("/process", response_model=MasteringResponse)
async def process_mastering(
    target: UploadFile = File(...),
    reference: Union[UploadFile, str, None] = File(None),
    preset: Optional[str] = Form(None)
):
    """
    Masters audio using Matchering 2.0.
    
    - **target**: The track to be mastered.
    - **reference**: (Optional) A reference track to match.
    - **preset**: (Optional) If no reference is uploaded, use a preset (e.g., "neutral").
    """
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save target file
    target_path = UPLOAD_DIR / f"target_{target.filename}"
    await file_io.save_upload_file(target, target_path)
    
    reference_path_str = None
    
    # Handle reference file
    # Check if reference is actually an UploadFile (and not an empty string or None)
    if isinstance(reference, UploadFile):
        # Save reference file
        ref_path = UPLOAD_DIR / f"ref_{reference.filename}"
        await file_io.save_upload_file(reference, ref_path)
        reference_path_str = str(ref_path)
    elif isinstance(reference, str):
        # If it's a string (e.g. empty string from form), ignore it
        pass
    
    try:
        # Run mastering
        output_path = mastering.process_audio(
            str(target_path),
            reference_path=reference_path_str,
            preset=preset
        )
        
        # Construct URL
        rel_path = Path(output_path).relative_to(OUTPUT_DIR)
        url = f"/outputs/{rel_path}"
        
        return MasteringResponse(
            status="success",
            mastered_url=url,
            message="Mastering completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mastering failed: {str(e)}")
