import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.workflow.graph import run_resolution_flow
from src.db.store import db

# Page configuration
st.set_page_config(
    page_title="ResolveX AI — AI-OPS v4.8",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit Chrome Elimination CSS (clean edge-to-edge canvas)
st.markdown("""
<style>
    /* Hide Streamlit default UI chrome */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Edge-to-edge container */
    .block-container {
        padding: 0rem !important;
        margin: 0rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    .stApp {
        background-color: #faf8ff !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        min-height: 2800px !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the pixel-perfect Stitch HTML interface
html_path = ROOT_DIR / "frontend" / "index.html"
if html_path.exists():
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=2800, scrolling=True)
else:
    st.error("Frontend template missing.")
