# # pages/1_Admin_Studio.py

# import streamlit as st
# import random
# import json
# import os
# import traceback
# from PIL import Image
# from utils.ai_engine import call_gemini_batch
# from utils.pdf_generator import create_unified_catalog
# from utils.gdrive_helper import upload_to_drive

# st.set_page_config(page_title="Admin | Catalog Creator", layout="wide")

# # --- SETTINGS ---
# FOLDER_ID = "18PR9msRprpjjwFr5aHNIZfUonUzTZyEM" 
# DB_PATH = "database/collections.json"

# os.makedirs("database", exist_ok=True)

# STYLE_PROMPTS = [
#     "A high-end flat lay of a folded shirt using this fabric, professional lighting.",
#     "Macro shot showing individual threads and linen slubs of this exact weave.",
#     "A male model wearing a tailored shirt made from this cloth, studio background.",
#     "A lifestyle shot of this fabric draped over a designer chair in a bright room."
# ]

# def save_to_index(name, link):
#     data = {}
#     if os.path.exists(DB_PATH):
#         try:
#             with open(DB_PATH, 'r') as f:
#                 data = json.load(f)
#         except json.JSONDecodeError:
#             data = {}
#     data[name] = {"pdf_link": link}
#     with open(DB_PATH, 'w') as f:
#         json.dump(data, f, indent=4)

# # --- UI ---
# st.title("🏭 Bulk Collection Creator")

# col_name = st.text_input("Collection Name", placeholder="e.g. Lakshya")
# files = st.file_uploader("Upload Patterns", accept_multiple_files=True, type=['png', 'jpg'])
# submit = st.button("Start Heavy Processing ✨", type="primary")

# if submit:
#     if not col_name:
#         st.error("Please enter a collection name.")
#     elif len(files) < 2:
#         st.error(f"Please upload at least 2 patterns.")
#     else:
#         try:
#             with st.status("🏗️ Building your Catalog...", expanded=True) as status:
                
#                 # 1. Selection
#                 st.write("🎲 Picking 2 designs for AI magic...")
#                 selected_for_ai = random.sample(files, 2)
                
#                 # 2. AI Generation
#                 st.write("🧠 Calling Gemini for High-Fidelity Visuals (8 steps)...")
#                 ai_assets = []
#                 progress_bar = st.progress(0)
                
#                 count = 0
#                 for sample in selected_for_ai:
#                     sample_img = Image.open(sample)
#                     for style in STYLE_PROMPTS:
#                         count += 1
#                         st.write(f"Generating Image {count}/8...")
#                         gen_img = call_gemini_batch(sample_img, style)
#                         if gen_img:
#                             ai_assets.append(gen_img)
#                         progress_bar.progress(count / 8)

#                 # 3. PDF Creation
#                 if len(ai_assets) > 0:
#                     st.write("📄 Binding Unified PDF...")
#                     final_pdf = create_unified_catalog(ai_assets, files, col_name)

#                     # 4. Single Upload & Index 
#                     st.write("☁️ Uploading to Google Drive...")
#                     gdrive_link = upload_to_drive(final_pdf, f"{col_name}_Catalog.pdf", FOLDER_ID)
                    
#                     if gdrive_link:
#                         save_to_index(col_name, gdrive_link)
#                         status.update(label="✅ Catalog Ready & Indexed!", state="complete")
#                         st.success(f"Successfully processed **{col_name}**. [View PDF]({gdrive_link})")
#                     else:
#                         st.error("Upload failed. Verify Google Drive credentials.")
#                 else:
#                     st.error("❌ AI failed to generate images.")
#                     status.update(label="❌ Process Failed", state="error")

#         except Exception as e:
#             st.error(f"An unexpected error occurred: {e}")
#             st.code(traceback.format_exc())
            
import streamlit as st
import random
import json
import os
import traceback
from PIL import Image
from utils.ai_engine import call_gemini_batch, crop_cad # Added crop_cad here
from utils.pdf_generator import create_unified_catalog
from utils.gdrive_helper import upload_to_drive

st.set_page_config(page_title="Admin | Catalog Creator", layout="wide")

FOLDER_ID = "18PR9msRprpjjwFr5aHNIZfUonUzTZyEM" 
DB_PATH = "database/collections.json"
os.makedirs("database", exist_ok=True)

MODEL_PROMPT = "A professional fashion studio shot of a handsome white male model from the waist up, wearing a tailored shirt made from this cloth. Focus on the shirt fit and texture. Half body shot."
FLATLAY_PROMPT = "A high-end flat lay of a folded shirt using this fabric, professional lighting."

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

def save_to_index(name, link):
    data = {}
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r') as f: data = json.load(f)
        except: data = {}
    data[name] = {"pdf_link": link}
    with open(DB_PATH, 'w') as f: json.dump(data, f, indent=4)

st.title("🏭 Bulk Collection Creator")

col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name", value="RAMGOPAL FASHION FABRICS")
    col_name = st.text_input("Collection Name", placeholder="")
with col2:
    brand_logo = st.file_uploader("Upload Company Logo", type=['jpg', 'jpeg', 'png'])

files = st.file_uploader("Upload CAD Patterns", accept_multiple_files=True, type=['png', 'jpg'])
submit = st.button("Generate Branded Catalog ✨", type="primary")

if submit and col_name and files:
    try:
        with st.status("🏗️ Building Branded Catalog...", expanded=True) as status:
            
            # 1. Selection: Pick ONE CAD and crop it for purity
            target_cad_file = files[0]
            full_cad_img = Image.open(target_cad_file)
            top_design, bottom_design = crop_cad(full_cad_img)
            
            ai_assets = []
            
            # 2. Generation Loop (3 images from 1 CAD)
            st.write("🕺 Generating Hero Model Shot (Design 1)...")
            hero = call_gemini_batch(top_design, MODEL_PROMPT)
            if hero: ai_assets.append(hero)
            
            st.write("👕 Generating First Flatlay (Design 1)...")
            flat1 = call_gemini_batch(top_design, FLATLAY_PROMPT)
            if flat1: ai_assets.append(flat1)
            
            st.write("👕 Generating Second Flatlay (Design 2)...")
            flat2 = call_gemini_batch(bottom_design, FLATLAY_PROMPT)
            if flat2: ai_assets.append(flat2)

            # 3. Logo Handling
            logo_path = None
            if brand_logo:
                logo_path = f"temp_logo.{brand_logo.name.split('.')[-1]}"
                with open(logo_path, "wb") as f:
                    f.write(brand_logo.getbuffer())

            # 4. Final PDF & Upload
            if len(ai_assets) == 3:
                final_pdf = create_unified_catalog(ai_assets, files, col_name, company_name, logo_path)
                gdrive_link = upload_to_drive(final_pdf, f"{col_name}_Catalog.pdf", FOLDER_ID)
                
                if gdrive_link:
                    save_to_index(col_name, gdrive_link)
                    status.update(label="✅ Success!", state="complete")
                    st.success(f"Branded Catalog ready: [View]({gdrive_link})")
            else:
                st.error("AI failed to generate images.")
                
    except Exception as e:
        st.error(f"Error: {e}")