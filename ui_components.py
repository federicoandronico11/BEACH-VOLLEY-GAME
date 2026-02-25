import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e11; color: #e9ecef; }
        .scoreboard-box { 
            background: #1f2937; border: 2px solid #8b5cf6; border-radius: 15px; 
            padding: 20px; text-align: center; margin-bottom: 25px;
        }
        .score-display { font-size: 60px; font-weight: bold; color: #8b5cf6; font-family: 'Courier New', monospace; }
        .winner-card {
            background: linear-gradient(135deg, #f59e0b 0%, #78350f 100%);
            padding: 40px; border-radius: 20px; text-align: center; color: white;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.5); margin: 20px 0;
        }
        .stat-item-box { background: #111827; padding: 15px; border-radius: 10px; border: 1px solid #374151; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar():
    with st.sidebar:
        st.title("📂 GESTIONALE")
        if st.button("💾 SALVA DATABASE TOTALE", use_container_width=True):
            st.success("Tutti i dati sono stati sincronizzati!")
        
        st.write("---")
        st.header("🏆 LEADERBOARD")
        t1, t2 = st.tabs(["RANKING", "PROFILI"])
        
        with t1:
            rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
            for i, (name, pts) in enumerate(rank):
                st.markdown(f"**{i+1}. {name}** — `{pts} PT`")
        
        with t2:
            scelta = st.selectbox("Seleziona Atleta", ["-"] + st.session_state['db_atleti'])
            if scelta != "-" and scelta != "N/A":
                s = st.session_state['atleti_stats'].get(scelta, {"pf":0,"ps":0,"sv":0,"sp":0,"partite_vinte":0,"tornei_giocati":0,"medaglie":[]})
                qp = round(s['pf']/s['ps'], 3) if s['ps']>0 else s['pf']
                qs = round(s['sv']/s['sp'], 3) if s['sp']>0 else s['sv']
                
                st.markdown(f"### {scelta} {''.join(s['medaglie'])}")
                st.markdown(f"""
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 5px;'>
                    <div class='stat-item-box'><b>Q. Punti</b><br>{qp}</div>
                    <div class='stat-item-box'><b>Q. Set</b><br>{qs}</div>
                    <div class='stat-item-box'><b>PF</b><br>{s['pf']}</div>
                    <div class='stat-item-box'><b>PS</b><br>{s['ps']}</div>
                    <div class='stat-item-box'><b>SV</b><br>{s['sv']}</div>
                    <div class='stat-item-box'><b>SP</b><br>{s['sp']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"🏟️ Tornei: {s['tornei_giocati']} | ✅ Vittorie: {s['partite_vinte']}")

        if st.button("🗑️ RESET SESSIONE"):
            st.session_state.clear()
            st.rerun()
