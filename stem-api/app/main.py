import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import stems, analysis, mastering
from app.config import OUTPUT_DIR

app = FastAPI(title="Music Stem Separation & Analysis API")

# Mount outputs directory to serve generated files
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

app.include_router(stems.router)
app.include_router(analysis.router)
app.include_router(mastering.router)

@app.get("/")
async def root():
    return {"message": "Stem Extraction API is running. Use POST /stems/extract to separate audio."}
