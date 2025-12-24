from pydantic import BaseModel
from typing import Dict, Optional

class StemResponse(BaseModel):
    status: str
    model: str
    stems: Dict[str, str]
    processing_time: float
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    filename: str
    bpm: int
    key: str
    scale: str
    loudness: float
    danceability: float
    dynamic_complexity: float

class MasteringResponse(BaseModel):
    status: str
    mastered_url: str
    message: Optional[str] = None
