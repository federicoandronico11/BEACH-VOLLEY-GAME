import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #ffffff; }
        h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; text-align: center; }
        .mega-counter { background: linear-gradient(180deg, #111, #000); border: 3px solid #9370DB; border-radius: 20px; padding: 30px; text-align: center; margin: 20px 0; }
        .counter-val { font-size: 5rem; font-weight: 900; color: #00ff00; line-height: 1; }
        .ranking-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #222; }
        .bracket-box { background: #111; border: 2px solid #4B0082; border-radius: 15px; padding: 20px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar_ranking():
    with st.sidebar:
        st.title("📊 LIVE RANKING")
        sorted_rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
        for i, (name, pts) in enumerate(sorted_rank):
            st.markdown(f"<div class='ranking-row'><span>{name}</span><span>{pts} PT</span></div>", unsafe_allow_html=True)
        st.write("---")
        if st.button("🗑️ RESET TOTALE"):
            st.session_state.clear()
            st.rerun()
