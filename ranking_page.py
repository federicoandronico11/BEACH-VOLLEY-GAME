import streamlit as st

def show_ranking():
    st.title("🏆 Hall of Fame")
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    
    if not rank: st.info("Nessun dato nel ranking."); return

    # Podio Visivo
    st.markdown('<div class="podium-container">', unsafe_allow_html=True)
    if len(rank) > 1: st.markdown(f'<div class="step" style="background:#c0c0c0; height:120px;">🥈<br>{rank[1][0]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step" style="background:#ffd700; height:180px;">🥇<br>{rank[0][0]}</div>', unsafe_allow_html=True)
    if len(rank) > 2: st.markdown(f'<div class="step" style="background:#cd7f32; height:80px;">🥉<br>{rank[2][0]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    for name, pts in rank:
        with st.expander(f"📊 {name} - {pts} Punti"):
            s = st.session_state.atleti_stats.get(name, {})
            if s:
                st.write(f"Vinte: {s['v']} | Perse: {s['p']}")
                st.line_chart(s['history'])
