import streamlit as st

def show_podium():
    st.title("🏆 HALL OF FAME")
    rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
    if not rank:
        st.info("Nessun dato disponibile nel ranking."); return

    st.markdown("""
        <style>
        .podium { display: flex; align-items: flex-end; justify-content: center; height: 250px; gap: 15px; margin-bottom: 50px; }
        .step { text-align: center; width: 120px; color: white; border-radius: 10px 10px 0 0; padding-bottom: 10px; }
        .gold { background: #ffd700; height: 200px; color: black; box-shadow: 0 0 20px #ffd700; }
        .silver { background: #c0c0c0; height: 150px; color: black; }
        .bronze { background: #cd7f32; height: 100px; color: black; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='podium'>", unsafe_allow_html=True)
    if len(rank) > 1: st.markdown(f"<div class='step silver'>🥈<br>{rank[1][0]}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='step gold'>🥇<br>{rank[0][0]}</div>", unsafe_allow_html=True)
    if len(rank) > 2: st.markdown(f"<div class='step bronze'>🥉<br>{rank[2][0]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    for name, pts in rank:
        if st.button(f"👤 Scheda Atleta: {name} ({pts} PT)", key=f"btn_{name}", use_container_width=True):
            st.session_state.search_atleta = name
            st.rerun()
