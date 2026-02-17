import aiofiles
from fastapi import UploadFile
from pathlib import Path
import shutil

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """Saves an uploaded file to the destination path."""
    try:
        async with aiofiles.open(destination, 'wb') as out_file:
            while content := await upload_file.read(1024 * 1024):  # Read in 1MB chunks
                await out_file.write(content)
    except Exception as e:
        # Fallback for synchronous file-like objects if aiofiles fails or for safety
        upload_file.file.seek(0)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
    return destination
