import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000; color: #fff; }
        .mega-counter { background: linear-gradient(180deg, #111, #000); border: 2px solid #9370DB; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; }
        .ranking-row { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 5px 0; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.header("📊 RANKING")
        rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
        for name, pts in rank:
            st.markdown(f"<div class='ranking-row'><span>{name}</span><span>{pts} PT</span></div>", unsafe_allow_html=True)
        st.write("---")
        st.header("🏅 ALBO D'ORO")
        for entry in reversed(st.session_state['albo_oro']):
            st.write(entry)
        if st.button("🗑️ RESET TOTALE"):
            st.session_state.clear()
            st.rerun()
