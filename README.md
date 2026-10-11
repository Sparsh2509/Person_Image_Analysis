# 👤 FestFit — Personal Face & Fashion Profile Analysis

A standalone Streamlit demo for FestFit that demonstrates AI-powered personal fashion profiling directly from an uploaded photo of a person using Groq Vision.

---

## 🌟 Features

- **Photo Upload**: Upload portrait/headshots or full-body pictures (JPG, JPEG, PNG).
- **Direct Image Vision**: Streams the uploaded image bytes directly to Groq Vision (`qwen/qwen3.8-27b`) as a base64 Data URI.
- **5 Extracted Fashion Dimensions**:
  1. **Face Shape**: Oval, Round, Square, Heart, Diamond, Oblong, or Unknown.
  2. **Body Type**: Rectangle, Hourglass, Pear, Apple, Inverted Triangle, or `Unknown` (safely returns `Unknown` if only the face/headshot is visible).
  3. **Recommended Colors**: 3–5 flattering colors rendered as visual colored swatches.
  4. **Recommended Styles**: 1–3 fashion aesthetics (Casual, Formal, Traditional, Western, Indo-Western).
  5. **Hairstyle Suggestions**: 2–4 hairstyles that flatter the determined face shape.
- **Side-by-Side Presentation**: Displays the uploaded photo on the left and the 5 profile cards on the right.
- **Dual API Key Fallback**: Automatic failover from `GROQ_API_KEY_1` to `GROQ_API_KEY_2` on rate limits.

---

## 📋 Fixed Categories Reference

### 1. Face Shape
`Oval`, `Round`, `Square`, `Heart`, `Diamond`, `Oblong`, `Unknown`

### 2. Body Type
`Rectangle`, `Hourglass`, `Pear`, `Apple`, `Inverted Triangle`, `Unknown`  
*(Returns `Unknown` when only the head/face is visible)*

### 3. Recommended Colors (15 Allowed Colors)
`Black`, `White`, `Navy Blue`, `Blue`, `Grey`, `Beige`, `Brown`, `Maroon`, `Olive Green`, `Pastel Pink`, `Red`, `Green`, `Cream`, `Lavender`, `Mustard Yellow`

### 4. Recommended Styles (5 Allowed Styles)
`Casual`, `Formal`, `Traditional`, `Western`, `Indo-Western`

### 5. Hairstyle Suggestions (9 Allowed Hairstyles)
`Short Hair`, `Medium Hair`, `Long Hair`, `Side-Parted Hair`, `Wavy Hair`, `Curly Hair`, `Layered Hair`, `Fringe/Bangs`, `Tied-Back Hair`

---

## 🚀 Quickstart & Setup

### 1. Navigate to the Folder
```bash
cd person_face_analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Groq API keys:
```env
GROQ_API_KEY_1=gsk_your_primary_key_here
GROQ_API_KEY_2=gsk_your_backup_key_here
GROQ_VISION_MODEL=qwen/qwen3.8-27b
```

### 4. Run the Streamlit Demo
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.
