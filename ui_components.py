import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        .dazn-card {
            background: #1e1e1e; border-left: 5px solid #e10600;
            border-radius: 4px; padding: 10px; margin-bottom: 10px;
        }
        .team-row { display: flex; justify-content: space-between; font-weight: bold; padding: 5px; }
        .red { color: #ff4b4b; } .blue { color: #0072ff; }
        .stat-delta-up { color: #00ff00; } .stat-delta-down { color: #ff0000; }
        </style>
    """, unsafe_allow_html=True)

def athlete_selector(label, key):
    """Input atleta con suggerimenti da quelli esistenti"""
    options = [""] + st.session_state.db_atleti
    return st.selectbox(label, options=options, key=key)
