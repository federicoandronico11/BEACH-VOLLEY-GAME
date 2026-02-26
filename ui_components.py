# Nel tab 2 dei Profili:
s = st.session_state['atleti_stats'].get(scelta)
# Calcolo Quozienti con gestione divisione per zero
q_punti = f"{s['pf'] / s['ps']:.3f}" if s['ps'] > 0 else (str(s['pf']) if s['pf'] > 0 else "0.000")
q_set = f"{s['sv'] / s['sp']:.3f}" if s['sp'] > 0 else (str(s['sv']) if s['sv'] > 0 else "0.000")

st.markdown(f"""
<div class='stat-card'>
    <h4>📊 Analytics {scelta}</h4>
    <p><b>Quoziente Punti:</b> {q_punti}</p>
    <p><b>Quoziente Set:</b> {q_set}</p>
    <p><b>Punti Totali:</b> {s['pf']} Fatti / {s['ps']} Subiti</p>
    <p><b>Set Totali:</b> {s['sv']} Vinti / {s['sp']} Persi</p>
</div>
""", unsafe_allow_html=True)
