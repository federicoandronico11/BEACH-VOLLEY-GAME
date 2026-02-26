import streamlit as st

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background: #0a0a0c; color: #f2f2f2; font-family: 'Rajdhani', sans-serif; }
    
    /* Card Stile DAZN / Broadcast */
    .broadcast-card {
        background: linear-gradient(135deg, #16161a 0%, #1f1f24 100%);
        border-left: 6px solid #ff0000;
        border-radius: 4px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .team-name-red { color: #ff4b4b; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .team-name-blue { color: #4b89ff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .score-center { 
        background: #000; color: #fff; padding: 5px 15px; 
        font-size: 2rem; border-radius: 4px; border: 1px solid #333;
        font-family: 'monospace';
    }
    
    /* Podio Custom */
    .podio-wrap { display: flex; align-items: flex-end; justify-content: center; gap: 20px; padding: 50px 0; }
    .podio-item { text-align: center; width: 130px; border-radius: 5px 5px 0 0; color: #000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
