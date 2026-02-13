# FX Commit System – Product UX Spec

> **Amaç:**
> Realtime FX denemeyi (preview) timeline‑bazlı, güvenli ve backend‑uyumlu bir **commit** sürecine dönüştürmek.
> Kullanıcı DAW bilmeden otomasyon yapabilmeli; backend tarafında **Spotify Pedalboard** ile deterministik, offline render alınabilmeli.

---

## 1. Ürün Prensipleri (Non‑Negotiable)

1. **Preview ≠ Commit**  
   Realtime deneme karar içindir, final kalite backend render’dır.
2. **Her FX = 1 Primary Graph**  
   Grafik parametreyi değil, **duyulan sonucu** temsil eder.
3. **Tek otomasyon lane**  
   Aynı FX’te birden fazla teknik parametreye otomasyon YOK.
4. **Zaman aralığı açıkça seçilir**  
   (Tüm parça / seçili aralık / marker arası)
5. **Backend deterministic**  
   Frontend yalnızca grafik + parametre recipe gönderir.

---

## 2. Genel Kullanıcı Akışı (UX Flow)

```text
[Realtime Preview]
   ↓
[Commit FX]
   ↓
[Range Selection]
   ↓
[Static Apply | Automation Graph]
   ↓
[FX‑Specific Graph Edit]
   ↓
[Render Job → Backend]
```

### 2.1 Realtime Preview
- Knob / slider kontrolü
- A/B snapshot (max 2)
- Timeline yok

### 2.2 Commit Panel
- **Range:** Entire Track | Selected Range | Marker Between
- **Mode:** Static Apply | Automation

### 2.3 Automation Edit
- Breakpoint ekle / sil
- Segment türü: Hold / Linear / Curve
- Tüm FX’lerde **aynı etkileşim modeli**

---

## 3. FX Commit UX – Standart Veri Modeli

```json
{
  "fx": "lowpass",
  "range": { "start": 72.0, "end": 105.5 },
  "static_params": {
    "resonance": 0.7
  },
  "automation": {
    "param": "cutoff",
    "curve": [
      { "t": 72.0, "v": 2400 },
      { "t": 90.0, "v": 800 },
      { "t": 105.5, "v": 2400 }
    ]
  }
}
```

---

| FX | Primary Graph | Secondary | Secondary Grappler | Otomasyon | Static Parametreler | Backend Model |
|----|---------------|-----------|--------------------|-----------|--------------------|---------------|
| Pitch Shift | Time vs Semitones | — | **Pitch Slider/Knob** | Pitch | — | Pitch engine |
| Pan | Time vs L↔R | Goniometer | **Pan Handle** (L/R) | Pan | — | Gain split |
| Invert | Toggle event | Waveform mirror | **Toggle Switch** | — | — | y = −x |
| Resample | Sample density | — | **SR Menu/Slider** | — | Target SR | Offline SRC |

---

## 5. UX Güvenlik Kuralları (Anti‑Footgun)

- ❌ Aynı FX’te birden fazla parametre otomasyonu yok
- ❌ Teknik parametre (Q, Attack) lane’i açılmaz
- ✅ Sadece **1 algısal otomasyon lane**
- ✅ Static + Automation net ayrılır

---

## 6. Sonuç

Bu sistem:
- DAW bilmeyen kullanıcıyı korur
- Otomasyonu sezgisel yapar
- Backend’de Pedalboard ile birebir uygulanır
- Realtime deneme + offline final kaliteyi ayırır

> **Ürün mottosu:**  
> *Hear first. Decide visually. Render perfectly.*

---

**Bu doküman tek sayfa Product UX Spec olarak kullanılabilir.**

