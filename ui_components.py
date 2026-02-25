import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #ffffff; }
        .mega-counter { background: linear-gradient(180deg, #111, #000); border: 3px solid #9370DB; border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 20px; }
        .counter-val { font-size: 5rem; font-weight: 900; color: #00ff00; }
        .ranking-box { background: #111; padding: 10px; border-radius: 10px; border-left: 5px solid #9370DB; margin-bottom: 5px; }
        .bracket-box { background: #111; border: 2px solid #4B0082; border-radius: 15px; padding: 20px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar_ranking():
    with st.sidebar:
        st.header("🏆 RANKING GENERALE")
        if st.session_state['ranking_atleti']:
            # Ordina per punteggio decrescente
            sorted_rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
            for i, (name, pts) in enumerate(sorted_rank):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏐"
                st.markdown(f"""<div class='ranking-box'>{medal} <b>{name}</b><br><span style='color:#00ff00'>{pts} PT</span></div>""", unsafe_allow_html=True)
        else:
            st.info("Nessun dato nel ranking.")
            
        st.write("---")
        st.header("🏅 ALBO D'ORO")
        for trionfo in reversed(st.session_state['albo_oro']):
            st.write(trionfo)
            
        if st.button("🗑️ RESET DATI"):
            st.session_state.clear()
            st.rerun()
