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
    .st-emotion-cache-p4mowd { 
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
        border-radius: 0px; 
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

    /* --- LIVE SCOREBOARD CONTROLS --- */
    .btn-score {
        height: 80px !important;
        font-size: 2rem !important;
        border: 2px solid #333 !important;
        background: #1a1a1a !important;
        color: white !important;
    }
    
    .btn-score:active {
        transform: scale(0.95);
        border-color: #00ff85 !important;
    }

    .service-indicator {
        width: 15px;
        height: 15px;
        background: #00ff85;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #00ff85;
        margin-right: 10px;
    }

    .timer-display {
        font-family: 'monospace';
        font-size: 1.5rem;
        color: #ffd700;
        text-align: center;
        padding: 10px;
        background: rgba(0,0,0,0.3);
        border-radius: 5px;
        border: 1px solid #444;
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
    
    /* Bottoni Standard */
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

    /* --- AGGIUNTE PER PODIO E CARRIERA --- */
    .podium-container {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 15px;
        margin: 40px 0;
        height: 300px;
    }

    .podium-step {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 1px solid #333;
        border-radius: 10px 10px 5px 5px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 20px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        width: 160px;
        position: relative;
    }

    .podium-step:hover {
        border-color: #00ff85;
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0, 255, 133, 0.2);
    }

    .first { height: 260px; border-top: 6px solid #ffd700; order: 2; z-index: 2; }
    .second { height: 210px; border-top: 6px solid #c0c0c0; order: 1; }
    .third { height: 170px; border-top: 6px solid #cd7f32; order: 3; }

    .podium-rank {
        font-family: 'Oswald'; font-size: 3.5rem; font-weight: 900; line-height: 1; margin-bottom: 10px;
        background: -webkit-linear-gradient(#eee, #333); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .podium-name { font-size: 1.1rem; text-align: center; font-weight: bold; text-transform: uppercase; color: white; }

    .career-card {
        background: rgba(255, 255, 255, 0.03); border-left: 4px solid #00ff85; padding: 15px; margin-bottom: 8px;
        border-radius: 0 4px 4px 0; display: flex; justify-content: space-between; align-items: center;
    }

    /* --- STILI AGGIUNTIVI PER IL NUOVO TABELLONE LIVE --- */
    .main-container-sb { background-color: rgba(0,0,0,0.4); padding: 20px; border-radius: 20px; border: 1px solid #333; }
    
    .team-red-bg { 
        background: linear-gradient(135deg, #ff4b4b, #a50000); 
        padding: 30px; border-radius: 15px; text-align: center; color: white; 
        border-bottom: 5px solid #ff0000; box-shadow: 0 10px 20px rgba(255,0,0,0.2);
    }
    
    .team-blue-bg { 
        background: linear-gradient(135deg, #0072ff, #003a80); 
        padding: 30px; border-radius: 15px; text-align: center; color: white; 
        border-bottom: 5px solid #0055ff; box-shadow: 0 10px 20px rgba(0,114,255,0.2);
    }
    
    .score-val-big { 
        font-size: 80px; font-weight: 900; font-family: 'monospace'; 
        line-height: 1; margin: 10px 0; text-shadow: 2px 2px 0px black;
    }
    
    .ball-icon-live { font-size: 35px; color: #fbff00; text-shadow: 0 0 15px #fbff00; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }

    .timer-box-live { 
        font-size: 25px; text-align: center; color: #00ffc3; 
        font-family: 'monospace'; padding: 10px; border: 1px solid #00ffc3; 
        border-radius: 10px; margin-bottom: 20px; background: rgba(0,255,195,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
