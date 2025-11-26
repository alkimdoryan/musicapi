# Music Stem Separation & Analysis API

A comprehensive audio processing API featuring stem separation, audio analysis, and mastering.

## Features

1.  **Stem Separation**: Uses **Hybrid Transformer Demucs (ht_demucs)** to separate audio into 4 stems: `vocals`, `drums`, `bass`, `other`.
2.  **Audio Analysis**: Uses **Essentia** to extract BPM, Key, Scale, Loudness, Danceability, and Dynamic Complexity.
3.  **Mastering**: Uses **Matchering 2.0** for reference-based or preset-based (reference-free) mastering.

## Setup (Recommended)

We strongly recommend using **Conda** to manage dependencies, especially for M1/M2 Macs.

1.  **Create the environment:**
    ```bash
    conda env create -f environment.yml
    ```

2.  **Activate the environment:**
    ```bash
    conda activate stem-api-env
    ```

3.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

## API Usage

Access the interactive Swagger UI at `http://127.0.0.1:8000/docs`.

### 1. Stem Separation
**POST** `/stems/extract`
- `audio_file`: The song to separate.
- `separation_model`: `ht_demucs` (default).

### 2. Audio Analysis
**POST** `/analysis/analyze`
- `file`: The audio file to analyze.
- **Returns**: BPM, Key, Scale, Loudness (LUFS), Danceability, etc.

### 3. Mastering
**POST** `/mastering/process`
- `target`: The track to master.
- `reference`: (Optional) A reference track to match.
- `preset`: (Optional) If no reference is provided, use `neutral` for a balanced master.

## Project Structure

- `app/routers`: API endpoints.
- `app/services`: Core logic for Demucs, Essentia, and Matchering.
- `outputs/`: Generated files (stems, mastered tracks).
- `uploads/`: Temporary storage for uploaded files.
