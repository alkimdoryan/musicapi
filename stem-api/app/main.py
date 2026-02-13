import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import stems, analysis, mastering, effects, timestretch, commit, upload
from app.config import OUTPUT_DIR

app = FastAPI(title="Music Stem Separation & Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount outputs directory to serve generated files
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

app.include_router(stems.router)
app.include_router(analysis.router)
app.include_router(mastering.router)

app.include_router(effects.router)
app.include_router(timestretch.router)
app.include_router(commit.router)
app.include_router(upload.router)

@app.get("/")
async def root():
    return {"message": "Stem Extraction API is running. Use POST /stems/extract to separate audio."}
