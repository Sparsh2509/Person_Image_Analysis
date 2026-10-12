"""Groq Vision analyzer for personal face, body, and style profiling."""

import base64
import io
import json
import os
import re
from typing import Dict, Any, List
from PIL import Image
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIStatusError, APIConnectionError

from constants import (
    VALID_SKIN_TONES,
    VALID_FACE_SHAPES,
    VALID_BODY_TYPES,
    VALID_RECOMMENDED_COLORS,
    VALID_RECOMMENDED_STYLES,
    VALID_HAIRSTYLES,
    normalize_skin_tone,
    normalize_face_shape,
    normalize_body_type,
    filter_colors,
    filter_styles,
    filter_hairstyles,
)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def get_groq_api_keys() -> List[str]:
    keys = []
    k1 = os.getenv("GROQ_API_KEY_1", "").strip()
    k2 = os.getenv("GROQ_API_KEY_2", "").strip()
    k_default = os.getenv("GROQ_API_KEY", "").strip()

    if k1:
        keys.append(k1)
    if k2 and k2 not in keys:
        keys.append(k2)
    if not keys and k_default:
        keys.append(k_default)
    return keys


def prepare_image_for_vision(image_file, max_dimension: int = 1280) -> str:
    img = Image.open(image_file)
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if w > max_dimension or h > max_dimension:
        scale = min(max_dimension / w, max_dimension / h)
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


SYSTEM_PROMPT = f"""You are a certified professional fashion stylist, personal image consultant, and face-shape expert for the FestFit platform.
Your task is to analyze an uploaded photo of a person and generate an accurate personalized fashion profile.

YOU MUST SELECT ONLY FROM THESE FIXED CATEGORIES:

1. face_shape (Select exactly 1):
{json.dumps(VALID_FACE_SHAPES)}
Guideline:
- Analyze jawline curvature, cheekbone width, forehead width, and face length:
  * Oval: Forehead slightly wider than chin, soft rounded jawline.
  * Round: Equal width and length, soft curved jawline and cheeks.
  * Square: Strong angular jawline, equal width at forehead, cheekbones, and jaw.
  * Heart: Wide forehead, pointed slender chin.
  * Diamond: Narrow forehead and jawline, widest at high cheekbones.
  * Oblong: Face length noticeably greater than width, straight cheek line.
  * Unknown: Face is not clearly visible, obscured, or heavily angled.

2. body_type (Select exactly 1):
{json.dumps(VALID_BODY_TYPES)}
CRITICAL RULE:
- ONLY estimate body type when the uploaded photo shows enough of the person's torso and body silhouette (bust/chest, waist, and hips).
- If only the face, headshot, shoulders, or neck is visible, you MUST return "Unknown".
- Never guess body type from a face-only photo.

3. skin_tone (Select EXACTLY 1 single skin tone value from this list):
{json.dumps(VALID_SKIN_TONES)}
SKIN TONE STYLING GUIDE:
- "Fair" and "Light":
  * Soft pastels (blush pink, powder blue, peach, mint, lilac, lavender).
  * Light neutrals and regal metallics: Ivory, cream, beige, champagne, off-white, silver, antique gold.
  * High-contrast bold hues: Deep maroon, navy blue, ruby red, and emerald green provide striking contrast.
- "Wheatish" and "Dusky":
  * Warm earth tones: Mustard, rust, terracotta, olive green, warm ochre, marigold.
  * Rich jewel tones: Deep maroon, wine, teal, royal blue, peacock green, warm gold.
  * Warm neutrals: Warm beige, tan, cream.
- "Deep":
  * Vibrant high-contrast colors: Crisp white, bright yellow, cobalt blue, fuchsia, orange.
  * Rich metallic gold, bronze, emerald, and deep jewel tones.
CRITICAL RULE: Return exactly ONE single skin tone string (e.g. "Wheatish" or "Fair"). Never return an array.

4. recommended_colors (Select 3 to 5 colors):
{json.dumps(VALID_RECOMMENDED_COLORS)}
Guideline:
- Base selection on the person's skin undertones (warm, cool, neutral), contrast, eye color, and hair color.
- Select the 3 to 5 most flattering colors that enhance their natural complexion.

5. recommended_styles (Select 1 to 3 styles):
{json.dumps(VALID_RECOMMENDED_STYLES)}
Guideline:
- Select 1 to 3 fashion aesthetics that complement their overall visual presence and proportions.

6. hairstyle_suggestions (Select 2 to 4 hairstyles):
{json.dumps(VALID_HAIRSTYLES)}
Guideline:
- Select 2 to 4 hairstyles specifically known to flatter and balance their determined face shape.
  * Round face: Medium Hair, Long Hair, Side-Parted Hair, Layered Hair.
  * Square face: Wavy Hair, Layered Hair, Side-Parted Hair.
  * Heart face: Medium Hair, Wavy Hair, Fringe/Bangs.
  * Oval face: Short Hair, Medium Hair, Long Hair, Wavy Hair, Tied-Back Hair.
  * Oblong face: Wavy Hair, Fringe/Bangs, Layered Hair.
  * Diamond face: Medium Hair, Side-Parted Hair, Wavy Hair.

OUTPUT FORMAT:
Return strictly a valid JSON object matching this structure:
{{
  "face_shape": "Oval",
  "body_type": "Unknown",
  "skin_tone": "Fair",
  "recommended_colors": ["Navy Blue", "White", "Olive Green"],
  "recommended_styles": ["Casual", "Indo-Western"],
  "hairstyle_suggestions": ["Short Hair", "Side-Parted Hair", "Wavy Hair"]
}}
"""


def analyze_person_photo(image_file) -> Dict[str, Any]:
    api_keys = get_groq_api_keys()
    if not api_keys:
        raise ValueError("No Groq API keys found. Please set GROQ_API_KEY_1 or GROQ_API_KEY in your .env file.")

    model_name = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
    image_data_uri = prepare_image_for_vision(image_file)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Analyze this person's photo. Determine face_shape (1 value), body_type (return Unknown if only face/head is visible), "
                        "skin_tone (EXACTLY 1 single value), recommended_colors (3-5 colors), recommended_styles (1-3 styles), "
                        "and hairstyle_suggestions (2-4 hairstyles). Return strictly a valid JSON object."
                    ),
                },
                {"type": "image_url", "image_url": {"url": image_data_uri}},
            ],
        },
    ]

    last_error = None
    for key_index, api_key in enumerate(api_keys, start=1):
        try:
            client = Groq(api_key=api_key, timeout=35.0)
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=600,
                response_format={"type": "json_object"},
            )

            raw_text = completion.choices[0].message.content or ""
            return parse_and_validate_analysis(raw_text)

        except RateLimitError as exc:
            last_error = f"Rate limit on API Key #{key_index}: {exc}"
            continue
        except APIStatusError as exc:
            last_error = f"Groq API Error {exc.status_code} on Key #{key_index}: {exc}"
            continue
        except (APIConnectionError, Exception) as exc:
            last_error = f"Connection error on Key #{key_index}: {exc}"
            continue

    raise RuntimeError(f"All Groq API keys failed. Details: {last_error}")


def parse_and_validate_analysis(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        data = {}

    face_shape = normalize_face_shape(data.get("face_shape", "Unknown"))
    body_type = normalize_body_type(data.get("body_type", "Unknown"))
    skin_tone = normalize_skin_tone(data.get("skin_tone", data.get("skin_tones", "Wheatish")))

    raw_colors = data.get("recommended_colors", [])
    if not isinstance(raw_colors, list):
        raw_colors = [str(raw_colors)] if raw_colors else []
    colors = filter_colors(raw_colors)

    raw_styles = data.get("recommended_styles", [])
    if not isinstance(raw_styles, list):
        raw_styles = [str(raw_styles)] if raw_styles else []
    styles = filter_styles(raw_styles)

    raw_hair = data.get("hairstyle_suggestions", [])
    if not isinstance(raw_hair, list):
        raw_hair = [str(raw_hair)] if raw_hair else []
    hairstyles = filter_hairstyles(raw_hair)

    return {
        "face_shape": face_shape,
        "body_type": body_type,
        "skin_tone": skin_tone,
        "recommended_colors": colors,
        "recommended_styles": styles,
        "hairstyle_suggestions": hairstyles,
    }
