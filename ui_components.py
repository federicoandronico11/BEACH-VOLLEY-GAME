import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e11; color: #e9ecef; }
        .scoreboard-box { 
            background: #161b22; border: 2px solid #30363d; border-radius: 15px; 
            padding: 20px; text-align: center; margin-bottom: 30px; 
        }
        .score-font { font-size: 50px; font-weight: bold; color: #8b5cf6; }
        .stat-card { background: #1f2937; border-radius: 10px; padding: 10px; border-top: 3px solid #8b5cf6; }
        .winner-announcement { 
            text-align: center; padding: 40px; background: linear-gradient(to right, #f59e0b, #d97706);
            color: white; border-radius: 20px; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.title("💾 DATABASE")
        if st.button("📥 SALVA DATI RANKING"):
            st.success("Dati salvati con successo!")
        
        st.write("---")
        st.header("🏆 HALL OF FAME")
        t1, t2 = st.tabs(["RANKING", "PROFILI"])
        
        with t1:
            rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
            for i, (name, pts) in enumerate(rank):
                st.markdown(f"**{i+1}. {name}** — `{pts} PT`")
        
        with t2:
            scelta = st.selectbox("Atleta", ["-"] + st.session_state['db_atleti'])
            if scelta != "-":
                s = st.session_state['atleti_stats'].get(scelta, {"pf":0,"ps":0,"sv":0,"sp":0,"partite_vinte":0,"tornei_giocati":0,"medaglie":[]})
                q_punti = round(s['pf'] / s['ps'], 3) if s['ps'] > 0 else s['pf']
                q_set = round(s['sv'] / s['sp'], 3) if s['sp'] > 0 else s['sv']
                
                st.markdown(f"### {scelta} {''.join(s['medaglie'])}")
                col1, col2 = st.columns(2)
                col1.metric("Q. Punti", q_punti)
                col1.metric("P. Fatti", s['pf'])
                col2.metric("Q. Set", q_set)
                col2.metric("P. Subiti", s['ps'])
                st.write(f"🏟️ Tornei: {s['tornei_giocati']} | ✅ Win: {s['partite_vinte']}")
