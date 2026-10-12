"""Streamlit Demo: FestFit AI Personal Fashion & Face Profile Analysis."""

import streamlit as st
from PIL import Image

from constants import COLOR_SWATCHES
from analyzer import analyze_person_photo, get_groq_api_keys

st.set_page_config(
    page_title="FestFit — Personal Fashion Profile",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .profile-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .profile-card-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        margin-bottom: 6px;
    }
    .profile-card-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F2937;
    }
    .profile-card-subtitle {
        font-size: 0.85rem;
        color: #6B7280;
        margin-top: 2px;
    }
    .swatches-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
    }
    .color-swatch-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .swatch-circle {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
    }
    .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }
    .style-tag {
        background-color: #EEF2FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .hair-tag {
        background-color: #FDF2F8;
        color: #9D174D;
        border: 1px solid #FBCFE8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("✨ FestFit — Personal AI Fashion Analysis")
st.markdown(
    "Upload your photo to discover your personalized fashion profile: **Face Shape**, **Body Silhouette**, "
    "**Skin Tone**, **Complimentary Colors**, **Recommended Styles**, and **Hairstyles**."
)
st.divider()

api_keys = get_groq_api_keys()
if not api_keys:
    st.warning("⚠️ No Groq API Key found. Please add `GROQ_API_KEY_1` or `GROQ_API_KEY` to your `.env` file.")

col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.subheader("📸 1. Upload Your Photo")
    uploaded_file = st.file_uploader(
        "Choose an image (JPG, JPEG, or PNG):",
        type=["jpg", "jpeg", "png"],
        help="You can upload either a face/portrait photo or a full-body outfit photo.",
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Photo Preview", use_container_width=True)

            analyze_button = st.button(
                "🔍 Analyze My Photo",
                type="primary",
                use_container_width=True,
                disabled=len(api_keys) == 0,
            )

            if analyze_button:
                with st.spinner("Analyzing your face shape, features, and color harmony with AI..."):
                    try:
                        uploaded_file.seek(0)
                        results = analyze_person_photo(uploaded_file)
                        st.session_state["analysis_results"] = results
                        st.session_state["analyzed_image"] = image
                    except Exception as exc:
                        st.error(f"Analysis failed: {str(exc)}")

        except Exception as e:
            st.error(f"Invalid or corrupted image file: {str(e)}")

    else:
        st.info("💡 Upload a photo above to begin. You can upload either a close-up portrait or a full-body picture.")
        if "analysis_results" in st.session_state:
            del st.session_state["analysis_results"]

with col_right:
    st.subheader("🎯 2. Your AI Fashion Profile")

    if "analysis_results" in st.session_state:
        res = st.session_state["analysis_results"]

        # Card 1: Face Shape
        face_shape = res.get("face_shape", "Unknown")
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">👤 Face Shape</div>
                <div class="profile-card-value">{face_shape}</div>
                <div class="profile-card-subtitle">Identified based on your jawline, forehead width, and cheek structure.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 2: Body Type
        body_type = res.get("body_type", "Unknown")
        body_subtitle = (
            "Analyzed from your visible torso and frame silhouette."
            if body_type != "Unknown"
            else "Only face/portrait visible in this photo. Upload a full-body picture to estimate body type."
        )
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">👗 Body Silhouette</div>
                <div class="profile-card-value">{body_type}</div>
                <div class="profile-card-subtitle">{body_subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 3: Skin Tone (Single String Value)
        skin_tone = res.get("skin_tone", "Wheatish")
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">✨ Skin Tone</div>
                <div class="profile-card-value">{skin_tone}</div>
                <div class="profile-card-subtitle">Identified based on facial complexion and natural undertones.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 4: Recommended Colors
        colors = res.get("recommended_colors", [])
        swatches_html = ""
        for color_name in colors:
            swatch_info = COLOR_SWATCHES.get(color_name, {"hex": "#4B5563", "text": "#FFFFFF", "border": "#4B5563"})
            bg_color = swatch_info["hex"]
            text_color = swatch_info["text"]
            border_color = swatch_info["border"]
            swatches_html += (
                f'<div class="color-swatch-pill" style="background-color: {bg_color}; color: {text_color}; border: 1.5px solid {border_color};">'
                f'<span class="swatch-circle" style="background-color: {text_color}; opacity: 0.85;"></span>'
                f'{color_name}'
                f'</div>'
            )

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">🎨 Recommended Color Palette</div>
                <div class="profile-card-subtitle">Colors that most complement your complexion and natural undertones:</div>
                <div class="swatches-container">{swatches_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 5: Recommended Styles
        styles = res.get("recommended_styles", [])
        styles_html = "".join([f'<span class="style-tag">{style}</span>' for style in styles])
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">✨ Recommended Fashion Styles</div>
                <div class="profile-card-subtitle">Fashion aesthetics that best match your frame and presence:</div>
                <div class="tags-container">{styles_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card 6: Hairstyle Suggestions
        hairstyles = res.get("hairstyle_suggestions", [])
        hair_html = "".join([f'<span class="hair-tag">{hair}</span>' for hair in hairstyles])
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-card-title">💇 Hairstyle Recommendations</div>
                <div class="profile-card-subtitle">Hair cuts and styles that flatter your {face_shape} face shape:</div>
                <div class="tags-container">{hair_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📋 View Structured Profile Data (JSON)"):
            st.json(res)

    else:
        st.markdown(
            """
            <div style="border: 2px dashed #D1D5DB; border-radius: 12px; padding: 48px 24px; text-align: center; color: #6B7280;">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">✨</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #374151;">Your results will appear here</div>
                <div style="font-size: 0.9rem; margin-top: 4px;">Upload a face or full-body photo on the left and click "Analyze My Photo" to generate your profile.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
