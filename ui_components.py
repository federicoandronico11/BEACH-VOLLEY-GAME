import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e11; color: #e9ecef; }
        .mega-counter { 
            background: linear-gradient(135deg, #6d28d9, #4c1d95); 
            border-radius: 20px; padding: 25px; text-align: center; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 25px;
        }
        .profile-card { 
            background: #1f2937; border: 1px solid #374151; 
            padding: 20px; border-radius: 15px; margin-bottom: 15px;
            border-left: 5px solid #8b5cf6;
        }
        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
        .stat-item { background: #111827; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #374151; }
        .medal-display { font-size: 1.8rem; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.header("🏆 HALL OF FAME")
        tab1, tab2 = st.tabs(["RANKING", "PROFILI"])
        
        with tab1:
            rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
            for i, (name, pts) in enumerate(rank):
                st.markdown(f"**{i+1}. {name}** — `{pts} PT`")
        
        with tab2:
            scelta = st.selectbox("Seleziona Atleta", ["-"] + st.session_state['db_atleti'])
            if scelta != "-":
                s = st.session_state['atleti_stats'].get(scelta, {"pf":0,"ps":0,"sv":0,"sp":0,"partite_vinte":0,"tornei_giocati":0,"medaglie":[]})
                st.markdown(f"""
                <div class='profile-card'>
                    <h3 style='margin:0;'>👤 {scelta}</h3>
                    <div class='medal-display'>{''.join(s['medaglie']) if s['medaglie'] else '🎖️ Debuttante'}</div>
                    <div class='stat-grid'>
                        <div class='stat-item'><b>Tornei</b><br>{s['tornei_giocati']}</div>
                        <div class='stat-item'><b>Win</b><br>{s['partite_vinte']}</div>
                        <div class='stat-item'><b>Set V</b><br>{s['sv']}</div>
                        <div class='stat-item'><b>Set P</b><br>{s['sp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")
        if st.button("🗑️ RESET SESSIONE", use_container_width=True):
            st.session_state.clear()
            st.rerun()
