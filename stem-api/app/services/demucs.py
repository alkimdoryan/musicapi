import asyncio
import shlex
import subprocess
from typing import Dict
from pathlib import Path
from app.config import OUTPUT_DIR

async def run_model(audio_path: str, model_name: str = "htdemucs") -> Dict[str, str]:
    """
    Runs Demucs separation.
    
    Args:
        audio_path: Path to the input audio file.
        model_name: Demucs model name (e.g., "htdemucs", "hdemucs_mmi", "mdx", "mdx_extra").
                    "demucs" in our API maps to "htdemucs" (default) or specific v3 models.
    
    Returns:
        Dictionary mapping stem names to their file paths.
    """
    # Map API model names to Demucs internal names if needed
    if model_name == "demucs":
        demucs_model = "htdemucs"
    elif model_name == "ht_demucs":
        demucs_model = "htdemucs"
    else:
        demucs_model = model_name

    output_path = OUTPUT_DIR / "demucs"
    output_path.mkdir(exist_ok=True, parents=True)

    # Construct command
    # demucs -n <model> -o <output_dir> <audio_file>
    cmd = f"demucs -n {demucs_model} -o {shlex.quote(str(output_path))} {shlex.quote(audio_path)}"
    
    # Run in a subprocess to avoid blocking the event loop
    # Note: Demucs is heavy, running it in a threadpool or process pool is better, 
    # but subprocess is easiest for CLI wrapping which Demucs supports well.
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Demucs failed: {stderr.decode()}")

    # Demucs output structure: <output_dir>/<model_name>/<track_name>/<stem>.wav
    track_name = Path(audio_path).stem
    model_output_dir = output_path / demucs_model / track_name
    
    stems = {}
    for stem in ["vocals", "drums", "bass", "other"]:
        stem_path = model_output_dir / f"{stem}.wav"
        if stem_path.exists():
            # Return relative path or full path as needed. 
            # For API response, we'll return the full path for now, 
            # but in a real app we'd return a URL.
            # We'll convert to a relative path from the static mount point.
            # Mount point is /outputs -> OUTPUT_DIR
            
            # Relative to OUTPUT_DIR
            rel_path = stem_path.relative_to(OUTPUT_DIR)
            stems[stem] = f"/outputs/{rel_path}"
    
    return stems
