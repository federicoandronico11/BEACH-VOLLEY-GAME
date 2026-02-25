import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #000; color: #fff; }
        .mega-counter { background: linear-gradient(180deg, #111, #000); border: 2px solid #9370DB; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; }
        .ranking-row { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 5px 0; }
        .profile-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        .medal-box { font-size: 1.5rem; letter-spacing: 5px; }
        .score-input { background: #222; border-radius: 5px; padding: 5px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.header("🏆 LEADERBOARD")
        tabs = st.tabs(["Ranking", "Profili"])
        
        with tabs[0]:
            rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
            for name, pts in rank:
                st.markdown(f"<div class='ranking-row'><span>{name}</span><span>{pts} PT</span></div>", unsafe_allow_html=True)
        
        with tabs[1]:
            atleta_scelto = st.selectbox("Cerca Atleta", ["-"] + st.session_state['db_atleti'])
            if atleta_scelto != "-":
                stats = st.session_state['atleti_stats'].get(atleta_scelto, {"pf":0,"ps":0,"sv":0,"sp":0,"partite":0,"medaglie":[]})
                st.markdown(f"""
                <div class='profile-card'>
                    <h4>{atleta_scelto}</h4>
                    <div class='medal-box'>{''.join(stats['medaglie']) if stats['medaglie'] else 'Zero Titoli'}</div>
                    <hr>
                    <p>🏟️ Partite: {stats['partite']}</p>
                    <p>🏐 Set: {stats['sv']}V / {stats['sp']}P</p>
                    <p>📈 Punti Fatti: {stats['pf']}</p>
                    <p>📉 Punti Subiti: {stats['ps']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")
        st.header("🏅 ALBO D'ORO")
        for entry in reversed(st.session_state['albo_oro']):
            st.write(entry)
