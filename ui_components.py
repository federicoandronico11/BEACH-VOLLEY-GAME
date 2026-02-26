import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700;900&family=Oswald:wght@500;700&display=swap');
    .stApp { background: #050505; color: white; font-family: 'Exo 2'; }
    
    /* Sidebar Leaderboard */
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff85; }
    
    .broadcast-card {
        background: linear-gradient(90deg, #111 0%, #1a1a1a 100%);
        border-left: 5px solid #00ff85; padding: 20px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .score-box { background: #00ff85; color: black; padding: 8px 20px; font-size: 1.8rem; font-weight: 900; border-radius: 4px; }
    
    .winner-reveal {
        animation: flash 1s infinite alternate;
        background: linear-gradient(45deg, #00ff85, #0072ff);
        padding: 60px; border-radius: 20px; text-align: center;
        box-shadow: 0 0 50px rgba(0, 255, 133, 0.5);
        color: black;
    }
    @keyframes flash { from { opacity: 0.8; } to { opacity: 1; transform: scale(1.02); } }
    
    .stButton>button { background: #00ff85 !important; color: black !important; font-weight: 900 !important; border-radius: 0px !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)
