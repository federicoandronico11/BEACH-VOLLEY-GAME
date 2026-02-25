import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e11; color: #e9ecef; }
        /* Dashboard TV Style */
        .match-card-broadcast {
            background: #1a1c23; border-radius: 12px; border-top: 5px solid #8b5cf6;
            margin-bottom: 15px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .broadcast-row { display: flex; align-items: center; padding: 12px 20px; color: white; font-weight: bold; font-size: 1.1rem; }
        .row-red { background: linear-gradient(90deg, #ff4b4b 0%, #1a1c23 85%); }
        .row-blue { background: linear-gradient(90deg, #0072ff 0%, #1a1c23 85%); }
        .stat-card { background: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
        .winner-card { background: linear-gradient(135deg, #f59e0b 0%, #78350f 100%); padding: 40px; border-radius: 20px; text-align: center; color: white; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.title("🏐 ZERO SKILLS PRO")
        nav = st.radio("SPOSTATI IN:", ["Torneo Live", "Hall of Fame 🏆"])
        st.write("---")
        
        if nav == "Torneo Live":
            t1, t2 = st.tabs(["RANKING", "PROFILI"])
            with t1:
                rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
                for i, (name, pts) in enumerate(rank):
                    st.markdown(f"**{i+1}. {name}** — `{pts} PT`")
            with t2:
                default_atleta = st.session_state.get('search_atleta', "-")
                atleti_list = ["-"] + st.session_state['db_atleti']
                idx = atleti_list.index(default_atleta) if default_atleta in atleti_list else 0
                scelta = st.selectbox("Seleziona Atleta", atleti_list, index=idx)
                if scelta != "-":
                    s = st.session_state['atleti_stats'].get(scelta, {"pf":0,"ps":0,"sv":0,"sp":0,"partite_vinte":0,"tornei_giocati":0,"medaglie":[]})
                    st.markdown(f"### {scelta} {''.join(s['medaglie'])}")
                    st.write(f"Vittorie: **{s['partite_vinte']}** | Tornei: **{s['tornei_giocati']}**")
                    qp = round(s['pf']/s['ps'], 3) if s['ps']>0 else s['pf']
                    st.write(f"Quoziente Punti: **{qp}**")
        return nav
