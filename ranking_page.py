import streamlit as st
import pandas as pd

def show_ranking_pro():
    st.title("🏆 HALL OF FAME & RANKING")
    
    # Podio Grafico
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    if len(rank) >= 3:
        c1, c2, c3 = st.columns([1,1,1])
        with c2: st.metric("🥇 1° Posto", rank[0][0], f"{rank[0][1]} PT")
        with c1: st.metric("🥈 2° Posto", rank[1][0], f"{rank[1][1]} PT")
        with c3: st.metric("🥉 3° Posto", rank[2][0], f"{rank[2][1]} PT")

    st.write("---")
    st.subheader("Classifica Generale")
    for i, (name, pts) in enumerate(rank):
        if st.button(f"{i+1}° {name} - {pts} PT", key=f"rank_{name}"):
            show_athlete_career(name)

def show_athlete_career(name):
    st.sidebar.markdown(f"## 👤 Carriera: {name}")
    s = st.session_state.atleti_stats.get(name, {"pf":0,"ps":0,"sv":0,"sp":0,"v":0,"p":0})
    
    # Calcolo Quozienti
    qp = round(s['pf']/max(1, s['ps']), 3)
    qs = round(s['sv']/max(1, s['sp']), 3)
    
    st.sidebar.write(f"Vinte: {s['v']} / Perse: {s['p']}")
    st.sidebar.write(f"Quoziente Punti: **{qp}**")
    st.sidebar.write(f"Quoziente Set: **{qs}**")
    # Qui potresti aggiungere uno st.line_chart per l'andamento
