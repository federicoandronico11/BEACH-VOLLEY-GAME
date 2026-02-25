import streamlit as st

def show_podium():
    st.markdown("""
        <style>
        .podium-container { display: flex; align-items: flex-end; justify-content: center; height: 300px; gap: 10px; margin-top: 50px; }
        .step { text-align: center; width: 150px; color: white; font-weight: bold; border-radius: 10px 10px 0 0; display: flex; flex-direction: column; justify-content: flex-end; padding-bottom: 20px; transition: transform 0.3s; cursor: pointer; }
        .step:hover { transform: translateY(-10px); }
        .gold { background: linear-gradient(0deg, #b8860b, #ffd700); height: 250px; box-shadow: 0 0 20px #ffd700; }
        .silver { background: linear-gradient(0deg, #707070, #c0c0c0); height: 180px; }
        .bronze { background: linear-gradient(0deg, #804a00, #cd7f32); height: 130px; }
        .athlete-name { font-size: 1.2rem; margin-bottom: 10px; text-shadow: 1px 1px 2px black; }
        .rank-num { font-size: 2.5rem; }
        </style>
    """, unsafe_allow_html=True)

    # Recupero e ordinamento atleti
    rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
    
    if not rank:
        st.warning("Nessun dato nel ranking disponibile.")
        return

    # Visualizzazione Podio
    st.markdown("<div class='podium-container'>", unsafe_allow_html=True)
    
    # Argento (2°)
    if len(rank) > 1:
        st.markdown(f"<div class='step silver'><div class='athlete-name'>{rank[1][0]}</div><div class='rank-num'>2</div></div>", unsafe_allow_html=True)
    
    # Oro (1°)
    st.markdown(f"<div class='step gold'><div class='athlete-name'>{rank[0][0]}</div><div class='rank-num'>1</div></div>", unsafe_allow_html=True)
    
    # Bronzo (3°)
    if len(rank) > 2:
        st.markdown(f"<div class='step bronze'><div class='athlete-name'>{rank[2][0]}</div><div class='rank-num'>3</div></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("📊 Classifica Completa e Palmares")

    # Lista Atleti cliccabile
    for i, (name, pts) in enumerate(rank):
        s = st.session_state['atleti_stats'].get(name, {"pf":0,"ps":0,"sv":0,"sp":0,"partite_vinte":0,"tornei_giocati":0,"medaglie":[]})
        with st.expander(f"{i+1}° - {name} ({pts} PT)"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Win Rate", f"{round((s['partite_vinte']/max(1, s['tornei_giocati']))*100)}%")
            c2.metric("Punti Fatti", s['pf'])
            c3.metric("Set Vinti", s['sv'])
            if st.button(f"Vedi Carriera di {name}", key=f"btn_{name}"):
                st.session_state.search_atleta = name # Passa il nome alla sidebar per la ricerca
                st.rerun()
