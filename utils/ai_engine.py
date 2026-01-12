# #utils/ai_engine.py

# import streamlit as st
# from google import genai
# from google.genai import types
# from PIL import Image
# from io import BytesIO

# def call_gemini_batch(input_img, style_prompt):
#     """
#     Calls Gemini image-preview model to generate an image
#     using the SAME logic as the working code.
#     """

#     # ✅ Image-capable Gemini model
#     MODEL_ID = "gemini-2.5-flash-image"
#     # or: "gemini-3-pro-image-preview"

#     client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

#     try:
#         response = client.models.generate_content(
#             model=MODEL_ID,
#             contents=[style_prompt, input_img],
#             config=types.GenerateContentConfig(
#                 response_modalities=["IMAGE"],
#                 image_config=types.ImageConfig(aspect_ratio="1:1")
#             )
#         )

#         # ✅ Same extraction logic as working app
#         if response.candidates:
#             for part in response.candidates[0].content.parts:
#                 if part.inline_data:
#                     return Image.open(BytesIO(part.inline_data.data))

#         # Fallback if model returns text instead of image
#         st.warning("Model returned text instead of image.")
#         st.write(response.text)
#         return None

#     except Exception as e:
#         st.error(f"AI Error: {e}")
#         return None





import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

def crop_cad(cad_pil_img):
    """Physically splits a 2-pattern CAD sheet into two separate images."""
    width, height = cad_pil_img.size
    # Crop top half (Pattern 1)
    top_half = cad_pil_img.crop((0, 0, width, height // 2))
    # Crop bottom half (Pattern 2)
    bottom_half = cad_pil_img.crop((0, height // 2, width, height))
    return top_half, bottom_half

def call_gemini_batch(input_img, style_prompt):
    MODEL_ID = "gemini-2.5-flash-image"
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[style_prompt, input_img],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="1:1")
            )
        )

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return Image.open(BytesIO(part.inline_data.data))
        return None
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None