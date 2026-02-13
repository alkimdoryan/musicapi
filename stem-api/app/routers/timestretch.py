
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
import os
import shutil
import tempfile
from app.services.time_stretch import stretch_r2, stretch_r3

router = APIRouter(tags=["Time Stretch"])


def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@router.post("/timestretch/process", summary="BPM Switch — R2 Fast")
async def timestretch_fast(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tempo_ratio: float = Form(..., description="Tempo ratio (1.2 = 20% faster)"),
    pitch_ratio: float = Form(1.0, description="Reserved, unused"),
):
    """
    Fast time-stretch using R2 engine (multi-threaded).
    Used by the frontend BPM Switch node.
    """
    if tempo_ratio <= 0:
        raise HTTPException(status_code=400, detail="tempo_ratio must be positive")

    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        input_path = tmp.name

    try:
        output_path = await run_in_threadpool(stretch_r2, input_path, tempo_ratio)

        background_tasks.add_task(cleanup_file, input_path)
        background_tasks.add_task(cleanup_file, output_path)

        return StreamingResponse(
            open(output_path, "rb"),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=stretched_{file.filename}"}
        )
    except Exception as e:
        cleanup_file(input_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/timestretch/process-hq", summary="BPM Switch — R3 Fine (HQ)")
async def timestretch_hq(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tempo_ratio: float = Form(..., description="Tempo ratio (1.2 = 20% faster)"),
    pitch_ratio: float = Form(1.0, description="Reserved, unused"),
):
    """
    High-quality time-stretch using R3 (finer) engine.
    Slower but produces the best results.
    """
    if tempo_ratio <= 0:
        raise HTTPException(status_code=400, detail="tempo_ratio must be positive")

    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        input_path = tmp.name

    try:
        output_path = await run_in_threadpool(stretch_r3, input_path, tempo_ratio)

        background_tasks.add_task(cleanup_file, input_path)
        background_tasks.add_task(cleanup_file, output_path)

        return StreamingResponse(
            open(output_path, "rb"),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=stretched_{file.filename}"}
        )
    except Exception as e:
        cleanup_file(input_path)
        raise HTTPException(status_code=500, detail=str(e))
