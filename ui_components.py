import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    .stApp { background: #0e1117; color: white; }
    .dazn-card {
        background: linear-gradient(90deg, #1a1a1a 0%, #252525 100%);
        border-left: 6px solid #e10600; border-radius: 6px;
        padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .team-name { font-weight: 800; font-size: 1.3rem; text-transform: uppercase; }
    .red-t { color: #ff4b4b; } .blue-t { color: #0072ff; }
    .score-display { background: #000; padding: 10px 20px; border-radius: 4px; font-size: 1.5rem; font-family: 'Courier New'; }
    .podium-container { display: flex; align-items: flex-end; justify-content: center; gap: 15px; padding: 40px 0; }
    .step { text-align: center; width: 120px; border-radius: 8px 8px 0 0; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
