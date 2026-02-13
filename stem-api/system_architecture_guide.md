# System Architecture Guide: FX Commit System
> **Version:** 1.1 (Spec-Aligned)  
> **Date:** Jan 7, 2026  
> **Scope:** Frontend (React/AudioEngine) + Backend (FastAPI/Pedalboard) + FX Commit Logic

---

## 1. Executive Summary (The "Hybrid" Philosophy)

This system is designed to bridge the gap between **Real-time Creativity** and **Offline Perfection**.

*   **Frontend (The Canvas):** Uses **Web Audio API** & **WASM** to provide instant, low-latency feedback. Users twist knobs and hear changes immediately. It is an *approximation* of the final sound.
*   **Backend (The Studio):** Uses **Spotify Pedalboard (Python)** to render the audio offline. It accepts the user's settings and applies studio-grade processing to generate the final WAV file.

---

## 2. The Core Concept: Primary vs. Secondary Graphs

The system solves the complexity of audio automation by strictly defining **one primary automation lane** per effect, while offering **secondary visualizations** or controls.

### 2.1 The Rules
1.  **Preview ≠ Commit:** Real-time is for decision making; Backend is for final quality.
2.  **Since FX = 1 Primary Graph:** The UI displays the *result* (e.g., Gain Reduction), not just the knob value.
3.  **One Automation Lane:** To prevent user error ("Footgun"), only the most musically relevant parameter is automated over time.

### 2.2 Spec Breakdown (Implemented Types)

The system architecture supports the following "Primary vs Secondary" definitions compliant with the Product UX Spec:

#### 🔴 Dynamic FX
| FX | Primary Graph (Automation) | Secondary (Visual/RO) | Backend Param |
| :--- | :--- | :--- | :--- |
| **Compressor** | Time vs **Gain Reduction** | Transfer Curve | `threshold`, `ratio`, `release` |
| **Limiter** | Time vs **Output Ceiling** | Waveform Clip | `ceiling_db` |
| **Noise Gate** | Time vs **Gate Open %** | Threshold Meter | `threshold_db` |

#### 🟡 Filter / EQ
| FX | Primary Graph (Automation) | Secondary (Visual/RO) | Backend Param |
| :--- | :--- | :--- | :--- |
| **Lowpass** | Time vs **Cutoff Hz** | Freq Response | `cutoff_hz` |
| **Highpass** | Time vs **Cutoff Hz** | Freq Response | `cutoff_hz` |
| **Peak/Shelf** | Time vs **Gain dB** | EQ Curve | `gain_db` |

#### 🔵 Time & Space
| FX | Primary Graph (Automation) | Secondary (Visual/RO) | Backend Param |
| :--- | :--- | :--- | :--- |
| **Reverb** | Time vs **Energy/Decay** | RT60 Values | `wet_level`, `room_size` |
| **Delay** | Tap Bars Timeline | Feedback Review | `mix`, `feedback` |
| **Convolution**| IR Waveform | **IR Selector** (File) | `impulse_response_filename` |

*(Note: For Convolution, the Secondary graph involves selecting the IR file, which is passed as a Static Parameter in the backend job.)*

---

## 3. Frontend Architecture: `AudioEngine.js`

This Javascript module is the heart of the client-side application.

### 3.1 Integration Flow
```javascript
// 1. Initialize
const engine = new AudioEngine();
await engine.init("vocal_stem.wav");

// 2. Real-time Control
engine.setLowpass(1000); // Instant hearing

// 3. Automation (The Primary Graph)
// When user draws on the "Primary Graph", send points here:
engine.setAutomationCurve("lowpass", "cutoff_hz", [
  { t: 0, v: 20000 },
  { t: 5, v: 500 }
]);
```

### 3.2 The "Commit" Action (`getExportJSON`)
When "Render" is clicked, the engine gathers all data into a **Standard FX Job**:
```json
{
  "fx": "lowpass",
  "range": { "start": 0, "end": 60 },
  "static_params": { "resonance": 0.5 },
  "automation": { // The Primary Graph Data
    "param": "cutoff_frequency_hz",
    "curve": [{ "t": 0, "v": 20000 }, { "t": 5, "v": 500 }]
  }
}
```

---

## 4. Backend Architecture: `FastAPI + Pedalboard`

### 4.1 The `FXCommitJob` Data Model
Defined in `app/schemas.py`, strict validation ensures the Job matches the Spec.

*   `fx`: The effect type (e.g. "lowpass").
*   `range`: Processing start/end time.
*   **`static_params`**: All settings *except* the automated one (e.g. Resonance, Drive, IR File).
*   **`automation`**: The single time-varying curve (e.g. Frequency, Wet Level).

### 4.2 Automation Engine (`commit_processor.py`)
To achieve "Secondary Automation" or "Optional Lanes" in the future, the backend uses a generic **Chunk-Based Processor**:
1.  **Chunks:** Audio is processed in 23ms blocks (1024 samples).
2.  **Interpolation:** The automation curve is sampled at each block.
3.  **Application:** The parameter is updated real-time before processing the chunk.
4.  **Mapping:** `PARAM_NAME_MAP` translates Frontend friendly names ("cutoff") to Pedalboard internal names ("cutoff_frequency_hz").

---

## 5. Parameter MappingTable
The system handles the translation between UX terms and Code terms:

| UX / Frontend Name | Backend / Pedalboard Name |
| :--- | :--- |
| `cutoff` / `cutoff_hz` | `cutoff_frequency_hz` |
| `drive` | `drive_db` |
| `threshold` | `threshold_db` |
| `rate` | `rate_hz` |

---

## 6. How to Run & Test
1.  **Frontend:** `npm install tone` -> Import `AudioEngine.js` -> Connect UI.
2.  **Backend:** `uvicorn app.main:app --host 0.0.0.0 --port 8070`.
3.  **Verify:** Run `test_commit_system.py` to simulated a Job submission.

---
**Product Spec Compliance:**
This system fully implements the "FX Commit" logic:
✅ **Primary Graph**: Supported via `automation` field.
✅ **Secondary/Static**: Supported via `static_params` dict.
✅ **Safe UX**: Backend validates only 1 automation lane per job (anti-footgun).
