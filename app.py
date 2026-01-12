# import streamlit as st
# from google import genai
# from google.genai import types
# from PIL import Image
# import io
# import time

# st.set_page_config(page_title="Pro Shirting AI", page_icon="👔")

# # 1. Setup
# API_KEY = st.secrets["GEMINI_API_KEY"]
# print("KEY IS" , API_KEY)
# client = genai.Client(api_key=API_KEY)

# st.title("👔 Pro Shirting Stylist (Gemini 1.5 Pro)")

# captured_image = st.camera_input("Capture Pattern")

# if captured_image:
#     img = Image.open(captured_image)
    
#     with st.spinner("Gemini Pro is analyzing the weave..."):
#         try:
#             # STEP 1: Analysis with Gemini 1.5 Pro
#             # This model is much more stable than the 2.0 experimental ones
#             analysis_prompt = "Analyze this fabric. Create a detailed prompt for an AI artist to generate a high-end 'flat-lay' photograph of a folded shirt made of this fabric, styled with matching luxury accessories."
            
#             analysis_response = client.models.generate_content(
#                 model="gemini-1.5-pro",
#                 contents=[analysis_prompt, img]
#             )
            
#             refined_prompt = analysis_response.text
#             st.info("Stylist's Vision: " + refined_prompt[:100] + "...")

#             # STEP 2: Generation with Imagen 3
#             # This turns the text description into an actual image
#             st.write("Generating your high-definition visual...")
#             image_response = client.models.generate_images(
#                 model="imagen-3.0-generate-002",
#                 prompt=refined_prompt,
#                 config=types.GenerateImagesConfig(
#                     number_of_images=1,
#                     aspect_ratio="1:1"
#                 )
#             )

#             # STEP 3: Display and Download
#             for generated in image_response.generated_images:
#                 final_img = Image.open(io.BytesIO(generated.image.image_bytes))
#                 st.image(final_img, caption="Your Curated Collection")
                
#                 # Download button for iPhone Save-to-Photos
#                 buf = io.BytesIO()
#                 final_img.save(buf, format="PNG")
#                 st.download_button(
#                     label="💾 Save Outfit to Photos",
#                     data=buf.getvalue(),
#                     file_name="ai_outfit.png",
#                     mime="image/png"
#                 )

#         except Exception as e:
#             if "429" in str(e):
#                 st.error("Quota reached. Please wait 60 seconds. Gemini Pro has stricter limits on the free tier.")
#             else:
#                 st.error(f"Error: {e}")




import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import time

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Textile AI Studio", 
    page_icon="👔", 
    layout="centered"
)

# Custom CSS for better mobile appearance
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stCameraInput { margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True) # <--- Use this instead

def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Restricted Access")
        pwd = st.text_input("Enter access password", type="password")

        if pwd:
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")

        st.stop()

check_access()

# --- 2. AUTHENTICATION & CLIENT ---
# Set this in your Streamlit Cloud Secrets or .env file
API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client = genai.Client(api_key=API_KEY)

# Track usage for the ₹100 budget
if "total_spent_inr" not in st.session_state:
    st.session_state.total_spent_inr = 159

# --- 3. UI - HEADER ---
st.title("👔 Textile AI Studio")
st.write("Professional Shirting Visualization Tool")

with st.sidebar:
    st.header("Studio Settings")
    model_choice = st.radio(
        "Model Selection",
        ["Nano Banana Pro (Gemini 3)", "Nano Banana (Gemini 2.5)"],
        help="Pro uses advanced reasoning for 4K quality. Nano is faster."
    )
    
    style_choice = st.selectbox(
        "Select Presentation Style",
        ["Curated Outfit Grid", "Single Folded (Macro)", "Model Studio Shot", "Inventory Stack"]
    )
    
    st.divider()
    st.metric("Budget Used", f"₹{st.session_state.total_spent_inr:.2f}", "of ₹1000.00")
    st.caption("Pro: ~₹11.20 / shot | Nano: ~₹3.20 / shot")

# --- 4. STYLE PROMPT ENGINE ---
STYLE_MAP = {
    "Curated Outfit Grid": "A top-down 'flat lay' of a curated menswear outfit. The centerpiece is a folded shirt made of the uploaded fabric. Surround it with leather shoes, a watch, and beige chinos on a concrete floor.",
    "Single Folded (Macro)": "An extreme close-up of a single, perfectly folded dress shirt. Show crisp collar details and the intricate weave texture of this exact fabric. Natural window lighting.",
    "Model Studio Shot": "A professional fashion photograph of a male model wearing a tailored shirt made of this fabric. Studio grey background, high-end commercial style.",
    "Inventory Stack": "A stack of 5 folded shirts, all made from this fabric pattern. Focus on the repeating pattern at the folded edges. Bright retail lighting."
}

# --- 5. IMAGE CAPTURE & GENERATION ---
captured_file = st.camera_input("Step 1: Capture Cloth Pattern")

if captured_file:
    # Prepare image for Gemini
    input_img = Image.open(captured_file)
    st.image(input_img, caption="Pattern Captured", width=150)
    
    if st.button("Step 2: Generate High-Def Asset ✨", type="primary"):
        selected_model = "gemini-3-pro-image-preview" if "Gemini 3" in model_choice else "gemini-2.5-flash-image"
        
        with st.spinner(f"Generating your image..."):
            try:
                # Core Generation Call
                response = client.models.generate_content(
                    model=selected_model,
                    contents=[STYLE_MAP[style_choice], input_img],
                    config=types.GenerateContentConfig(
                        response_modalities=['IMAGE'],
                        image_config=types.ImageConfig(aspect_ratio="1:1")
                    )
                )

                # Find the image in the response parts
                found_img = False
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        gen_img = Image.open(BytesIO(part.inline_data.data))
                        st.image(gen_img, caption="Generated Result", width='stretch')
                        
                        # Update Cost Tracker
                        cost = 11.20 if "Gemini 3" in model_choice else 3.20
                        st.session_state.total_spent_inr += cost
                        
                        # Download Button for iPhone 'Save to Photos'
                        buf = BytesIO()
                        gen_img.save(buf, format="PNG")
                        st.download_button(
                            label="💾 Save to Photos",
                            data=buf.getvalue(),
                            file_name=f"shirting_{int(time.time())}.png",
                            mime="image/png"
                        )
                        found_img = True
                
                if not found_img:
                    st.warning("The AI returned a description instead of an image. Try again.")
                    st.write(response.text)

            except Exception as e:
                if "429" in str(e):
                    st.error("Rate limit reached. Please wait 60 seconds. (Free tier limits)")
                else:
                    st.error(f"Something went wrong: {e}")

st.divider()
st.caption("Created by SUHANI!")