import streamlit as st
import json
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Textile AI Studio | Showroom",
    page_icon="👔",
    layout="centered"
)

# Custom CSS for a premium mobile look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #075E54; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 10px; padding: 10px; }
    .collection-card { border: 1px solid #ddd; padding: 20px; border-radius: 12px; margin-bottom: 20px; background-color: #f9f9f9; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING ---
DB_PATH = "database/collections.json"

def load_collections():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- 3. UI LAYOUT ---
st.title("👔 Textile AI Studio")
st.subheader("Digital Collection Showroom")

# Search Bar (Mobile Friendly)
search_query = st.text_input("🔍 Search for a collection...", placeholder="e.g., Lakshya, Linen Tube")

collections = load_collections()

if not collections:
    st.info("No collections found. Please use the Admin Studio to create your first catalog.")
else:
    # Filter collections based on search
    filtered_keys = [k for k in collections.keys() if search_query.lower() in k.lower()]

    if not filtered_keys:
        st.warning("No collections match your search.")
    else:
        for name in filtered_keys:
            pdf_link = collections[name].get("pdf_link", "#")
            
            # Display each collection in a "Card"
            with st.container():
                st.markdown(f"""
                <div class="collection-card">
                    <h3 style='margin-top:0;'>📦 {name}</h3>
                    <p style='color: #666;'>Full HD Lookbook & Technical Patterns</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Primary Action Button for Mobile
                # Tapping this opens the Google Drive PDF directly in the browser
                st.link_button(f"📄 Open {name} Catalog", pdf_link)
                
                # Secondary Help for WhatsApp Sharing
                st.caption(f"Tip: Long-press the button above to 'Copy Link' for WhatsApp.")
            
            st.divider()

st.caption("Designed by SUHANI | Professional Textile Visualization")