import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #050505; color: #ffffff; }
    
    /* Card DAZN Style */
    .dazn-match-card {
        background: linear-gradient(90deg, #111 0%, #1a1a1a 100%);
        border-left: 5px solid #e10600; border-radius: 4px;
        padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }
    .team-red { color: #ff4b4b; font-weight: 900; font-size: 1.2rem; }
    .team-blue { color: #0072ff; font-weight: 900; font-size: 1.2rem; }
    .score-badge { background: #333; padding: 5px 12px; border-radius: 4px; font-family: monospace; font-size: 1.2rem; }
    
    /* Podio */
    .podium-box { display: flex; align-items: flex-end; justify-content: center; gap: 10px; padding: 20px; }
    .gold { background: linear-gradient(180deg, #ffd700, #b8860b); height: 180px; width: 100px; text-align: center; border-radius: 8px 8px 0 0; }
    .silver { background: linear-gradient(180deg, #c0c0c0, #707070); height: 130px; width: 100px; text-align: center; border-radius: 8px 8px 0 0; }
    .bronze { background: linear-gradient(180deg, #cd7f32, #804a00); height: 90px; width: 100px; text-align: center; border-radius: 8px 8px 0 0; }
    </style>
    """, unsafe_allow_html=True)
