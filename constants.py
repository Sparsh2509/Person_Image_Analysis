"""Constants, allowed category lists, and color mappings for Person Face & Style Analysis."""

from typing import List, Dict

# 1. Face Shape (Allowed Values)
VALID_FACE_SHAPES: List[str] = [
    "Oval",
    "Round",
    "Square",
    "Heart",
    "Diamond",
    "Oblong",
    "Unknown",
]

# 2. Body Type (Allowed Values)
VALID_BODY_TYPES: List[str] = [
    "Rectangle",
    "Hourglass",
    "Pear",
    "Apple",
    "Inverted Triangle",
    "Unknown",
]

# 3. Recommended Colors (Allowed Values)
VALID_RECOMMENDED_COLORS: List[str] = [
    "Black",
    "White",
    "Navy Blue",
    "Blue",
    "Grey",
    "Beige",
    "Brown",
    "Maroon",
    "Olive Green",
    "Pastel Pink",
    "Red",
    "Green",
    "Cream",
    "Lavender",
    "Mustard Yellow",
]

# 4. Recommended Styles (Allowed Values)
VALID_RECOMMENDED_STYLES: List[str] = [
    "Casual",
    "Formal",
    "Traditional",
    "Western",
    "Indo-Western",
]

# 5. Hairstyle Suggestions (Allowed Values)
VALID_HAIRSTYLES: List[str] = [
    "Short Hair",
    "Medium Hair",
    "Long Hair",
    "Side-Parted Hair",
    "Wavy Hair",
    "Curly Hair",
    "Layered Hair",
    "Fringe/Bangs",
    "Tied-Back Hair",
]

# Color hex codes and text contrast colors for visual swatches
COLOR_SWATCHES: Dict[str, Dict[str, str]] = {
    "Black": {"hex": "#1A1A1A", "text": "#FFFFFF", "border": "#1A1A1A"},
    "White": {"hex": "#FFFFFF", "text": "#1A1A1A", "border": "#D1D5DB"},
    "Navy Blue": {"hex": "#0A192F", "text": "#FFFFFF", "border": "#0A192F"},
    "Blue": {"hex": "#2563EB", "text": "#FFFFFF", "border": "#2563EB"},
    "Grey": {"hex": "#6B7280", "text": "#FFFFFF", "border": "#6B7280"},
    "Beige": {"hex": "#D4C5B9", "text": "#332211", "border": "#B8A596"},
    "Brown": {"hex": "#5C4033", "text": "#FFFFFF", "border": "#5C4033"},
    "Maroon": {"hex": "#800020", "text": "#FFFFFF", "border": "#800020"},
    "Olive Green": {"hex": "#556B2F", "text": "#FFFFFF", "border": "#556B2F"},
    "Pastel Pink": {"hex": "#FFD1DC", "text": "#6B21A8", "border": "#F4A6B8"},
    "Red": {"hex": "#DC2626", "text": "#FFFFFF", "border": "#DC2626"},
    "Green": {"hex": "#16A34A", "text": "#FFFFFF", "border": "#16A34A"},
    "Cream": {"hex": "#FFFDD0", "text": "#4A3B18", "border": "#E8E2A7"},
    "Lavender": {"hex": "#E6E6FA", "text": "#3B1F70", "border": "#C7C7F2"},
    "Mustard Yellow": {"hex": "#E1AD01", "text": "#3B2A00", "border": "#C59600"},
}

# Lookup dictionaries for case-insensitive normalization
_FACE_SHAPE_LOOKUP = {item.lower(): item for item in VALID_FACE_SHAPES}
_BODY_TYPE_LOOKUP = {item.lower(): item for item in VALID_BODY_TYPES}
_COLOR_LOOKUP = {item.lower(): item for item in VALID_RECOMMENDED_COLORS}
_STYLE_LOOKUP = {item.lower(): item for item in VALID_RECOMMENDED_STYLES}
_HAIRSTYLE_LOOKUP = {item.lower(): item for item in VALID_HAIRSTYLES}


def normalize_face_shape(val: str) -> str:
    if not isinstance(val, str):
        return "Unknown"
    return _FACE_SHAPE_LOOKUP.get(val.strip().lower(), "Unknown")


def normalize_body_type(val: str) -> str:
    if not isinstance(val, str):
        return "Unknown"
    return _BODY_TYPE_LOOKUP.get(val.strip().lower(), "Unknown")


def filter_colors(colors: List[str]) -> List[str]:
    seen = set()
    res = []
    for c in colors:
        if isinstance(c, str):
            canonical = _COLOR_LOOKUP.get(c.strip().lower())
            if canonical and canonical not in seen:
                seen.add(canonical)
                res.append(canonical)
    # Ensure between 3 and 5 colors
    if len(res) < 3:
        # Fallback safe defaults if model provided fewer
        defaults = ["Navy Blue", "White", "Black"]
        for d in defaults:
            if d not in seen and len(res) < 3:
                res.append(d)
                seen.add(d)
    return res[:5]


def filter_styles(styles: List[str]) -> List[str]:
    seen = set()
    res = []
    for s in styles:
        if isinstance(s, str):
            canonical = _STYLE_LOOKUP.get(s.strip().lower())
            if canonical and canonical not in seen:
                seen.add(canonical)
                res.append(canonical)
    if not res:
        res = ["Casual"]
    return res[:3]


def filter_hairstyles(hairstyles: List[str]) -> List[str]:
    seen = set()
    res = []
    for h in hairstyles:
        if isinstance(h, str):
            canonical = _HAIRSTYLE_LOOKUP.get(h.strip().lower())
            if canonical and canonical not in seen:
                seen.add(canonical)
                res.append(canonical)
    if len(res) < 2:
        defaults = ["Medium Hair", "Side-Parted Hair"]
        for d in defaults:
            if d not in seen and len(res) < 2:
                res.append(d)
                seen.add(d)
    return res[:4]
