import streamlit as st
import pandas as pd

def render_all():
    st.title("Hall of Fame")
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    
    if not rank:
        st.warning("Nessun dato. Inizia un torneo per generare il ranking.")
        return

    # PODIO VISIVO
    st.markdown('<div class="podium-box">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2: st.markdown(f'<div class="gold">🥇<br><b>{rank[0][0]}</b><br>{rank[0][1]} PT</div>', unsafe_allow_html=True)
    if len(rank)>1:
        with col1: st.markdown(f'<div class="silver">🥈<br><b>{rank[1][0]}</b><br>{rank[1][1]} PT</div>', unsafe_allow_html=True)
    if len(rank)>2:
        with col3: st.markdown(f'<div class="bronze">🥉<br><b>{rank[2][0]}</b><br>{rank[2][1]} PT</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # LISTA ATLETI CLICCABILE
    st.subheader("Classifica Completa")
    for name, pts in rank:
        with st.expander(f"👤 {name} | {pts} Punti"):
            s = st.session_state.atleti_stats.get(name, {})
            if s:
                c1, c2, c3 = st.columns(3)
                c1.metric("Vittorie", s['v'], "📈")
                c2.metric("Sconfitte", s['p'], "📉", delta_color="inverse")
                c3.metric("Quoziente Set", round(s['sv']/max(1,s['sp']), 2))
                
                # Grafico di crescita
                if s['history']:
                    st.line_chart(s['history'])
