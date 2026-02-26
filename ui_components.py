import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700;900&family=Oswald:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #12121e, #050505);
        color: #ffffff;
        font-family: 'Exo 2', sans-serif;
    }

    /* Menu Hub FC 26 */
    .fc-tile {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 40px 20px;
        transition: all 0.3s ease;
        text-align: center;
        cursor: pointer;
    }
    .fc-tile:hover {
        background: rgba(0, 255, 133, 0.05);
        border-color: #00ff85;
        transform: scale(1.02);
    }

    /* Card Match Day */
    .broadcast-card {
        background: #1a1a1a;
        border-bottom: 4px solid #00ff85;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .team-red { color: #ff4b4b; font-weight: 900; font-size: 1.4rem; text-transform: uppercase; }
    .team-blue { color: #0072ff; font-weight: 900; font-size: 1.4rem; text-transform: uppercase; }
    .score-box { background: #000; padding: 10px 25px; font-size: 2rem; border-radius: 5px; font-family: 'monospace'; color: #00ff85; }

    /* Bottoni FC Style */
    .stButton>button {
        background: #00ff85 !important;
        color: #000 !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 0px !important;
        border: none !important;
        transition: 0.2s;
    }
    .stButton>button:hover { background: #ffffff !important; transform: skew(-5deg); }
    </style>
    """, unsafe_allow_html=True)
    import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@900&family=Oswald:wght@700&display=swap');
    .stApp { background: #050505; color: white; font-family: 'Exo 2'; }
    
    .broadcast-card {
        background: linear-gradient(90deg, #111 0%, #1a1a1a 100%);
        border-left: 5px solid #00ff85; padding: 20px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .score-box { background: #00ff85; color: black; padding: 8px 20px; font-size: 1.8rem; font-weight: 900; border-radius: 4px; }
    
    /* Animazione Vincitore FC 26 Style */
    .winner-reveal {
        animation: flash 1s infinite alternate;
        background: linear-gradient(45deg, #00ff85, #0072ff);
        padding: 60px; border-radius: 20px; text-align: center;
        box-shadow: 0 0 50px rgba(0, 255, 133, 0.5);
    }
    @keyframes flash { from { opacity: 0.8; } to { opacity: 1; transform: scale(1.02); } }
    
    .stButton>button { background: #00ff85 !important; color: black !important; font-weight: 900 !important; border-radius: 0px !important; }
    </style>
    """, unsafe_allow_html=True)
