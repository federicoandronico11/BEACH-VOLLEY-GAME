import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    /* Import Font Gaming */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700;900&family=Oswald:wght@500;700&display=swap');
    
    /* Layout Generale */
    .stApp { 
        background: radial-gradient(circle at 50% 50%, #121212 0%, #050505 100%);
        color: white; 
        font-family: 'Exo 2', sans-serif; 
    }

    /* --- SIDEBAR CUSTOM --- */
    [data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 2px solid #00ff85;
    }
    
    /* Expander della Carriera (Sidebar) */
    .st-emotion-cache-p4mowd { /* Classe specifica per l'expander */
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 255, 133, 0.2) !important;
        border-radius: 4px !important;
    }

    /* --- BROADCAST CARDS (MATCH DAY) --- */
    .broadcast-card {
        background: linear-gradient(90deg, #111 0%, #1a1a1a 100%);
        border-bottom: 4px solid #00ff85;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    
    .team-red { 
        color: #ff4b4b; 
        font-weight: 900; 
        font-size: 1.4rem; 
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(255, 75, 75, 0.3);
    }
    
    .team-blue { 
        color: #0072ff; 
        font-weight: 900; 
        font-size: 1.4rem; 
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(0, 114, 255, 0.3);
    }
    
    .score-box { 
        background: #000; 
        color: #00ff85; 
        padding: 10px 30px; 
        font-size: 2.2rem; 
        border-radius: 5px; 
        font-family: 'monospace'; 
        font-weight: bold;
        border: 1px solid #333;
    }

    /* --- TILES MENU HUB --- */
    .fc-tile {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0px; /* Taglio netto FC Style */
        padding: 40px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .fc-tile:hover {
        border-color: #00ff85;
        background: rgba(0, 255, 133, 0.08);
        transform: translateY(-8px) skew(-2deg);
        box-shadow: 0 15px 30px rgba(0, 255, 133, 0.1);
    }
    
    .fc-tile h2 {
        font-family: 'Oswald', sans-serif;
        font-size: 2rem;
        letter-spacing: 2px;
        color: #00ff85;
    }

    /* --- CELEBRAZIONE VINCITORE --- */
    .winner-reveal {
        background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
        padding: 60px;
        border-radius: 10px;
        text-align: center;
        color: black;
        box-shadow: 0 0 60px rgba(255, 215, 0, 0.6);
        animation: winner-glow 2s infinite alternate;
    }
    
    @keyframes winner-glow {
        from { box-shadow: 0 0 40px rgba(255, 215, 0, 0.4); }
        to { box-shadow: 0 0 80px rgba(255, 215, 0, 0.8); transform: scale(1.02); }
    }

    /* --- METRICHE E QUOZIENTI --- */
    [data-testid="stMetricValue"] {
        color: #00ff85 !important;
        font-family: 'monospace' !important;
        font-size: 1.8rem !important;
    }
    
    /* Bottoni */
    .stButton>button {
        background: #00ff85 !important;
        color: black !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 1rem 2rem !important;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background: white !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
