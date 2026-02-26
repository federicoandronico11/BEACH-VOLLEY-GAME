import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700;900&family=Oswald:wght@500;700&display=swap');

    /* Sfondo e Base */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #0f0f0f);
        color: #ffffff;
        font-family: 'Exo 2', sans-serif;
    }

    /* Menu a Mattonelle FC 26 Style */
    .fc-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        padding: 20px;
    }

    .fc-tile {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 30px;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .fc-tile:hover {
        background: rgba(0, 255, 133, 0.1); /* Verde Neon tipico FC */
        border-color: #00ff85;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 255, 133, 0.2);
    }

    .fc-tile h2 {
        font-family: 'Oswald', sans-serif;
        text-transform: uppercase;
        font-size: 1.8rem;
        margin-bottom: 10px;
        color: #00ff85;
    }

    /* Card Squadre Match Day */
    .match-card {
        background: linear-gradient(135deg, rgba(30,30,30,0.9) 0%, rgba(10,10,10,0.9) 100%);
        border-left: 8px solid #00ff85;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    .score-badge {
        background: #00ff85;
        color: #000;
        font-weight: 900;
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 1.5rem;
    }

    /* Bottone Professionale */
    .stButton>button {
        background: #00ff85 !important;
        color: #000 !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 0px !important; /* Taglio netto FC Style */
        border: none !important;
        padding: 15px 30px !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
