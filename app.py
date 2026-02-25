import streamlit as st
import pandas as pd

# 1. SETUP PAGINA
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'tournament_type' not in st.session_state: st.session_state['tournament_type'] = "Gironi + Eliminazione"

# 3. HEADER
st.title("ZERO SKILLS CUP")
st.write("Se hai 0 skills, sei nel posto giusto")

# 4. SIDEBAR - CONFIGURAZIONE E ISCRIZIONI
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    if st.session_state['phase'] == "Setup":
        st.session_state['tournament_type'] = st.radio(
            "Tipologia Tabellone:",
            ["Gironi + Eliminazione", "Solo Eliminazione Diretta"]
        )
        
        st.write("---")
        st.header("👥 Iscrizioni")
        with st.form("form_iscrizione", clear_on_submit=True):
            t_name = st.text_input("Nome Squadra")
            p1 = st.text_input("Giocatore 1")
            p2 = st.text_input("Giocatore 2")
            if st.form_submit_button("Aggiungi Team"):
                if t_name and p1 and p2:
                    entry = f"{t_name} ({p1}/{p2})"
                    if entry not in st.session_state['teams']:
                        st.session_state['teams'].append(entry)
                        st.success(f"Iscritto: {t_name}")
                else:
                    st.warning("Dati incompleti")

    st.write("---")
    st.write(f"Squadre iscritte: {len(st.session_state['teams'])}")
    for t in st.session_state['teams']:
        st.text(f"• {t}")

    # AVVIO TORNEO
    if len(st.session_state['teams']) >= 4 and st.session_state['phase'] == "Setup":
        if st.button("🚀 INIZIA TORNEO"):
            if st.session_state['tournament_type'] == "Gironi + Eliminazione":
                st.session_state['phase'] = "Gironi"
                lista = st.session_state['teams']
                for i in range(len(lista)):
                    for j in range(i + 1, len(lista)):
                        st.session_state['matches'].append({"A": lista[i], "B": lista[j], "Set_Finale": "2-0", "SA": 0, "SB": 0, "Fatto": False})
            else:
                st.session_state['phase'] = "Playoff"
                # Prepariamo subito le semifinali con i primi 4 iscritti
                top4 = st.session_state['teams'][:4]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top4[0], "B": top4[3], "V": None},
                    {"N": "Semi 2", "A": top4[1], "B": top4[2], "V": None}
                ]
            st.rerun()
            
    if st.button("🗑️ RESET TOTALE"):
        st.session_state.clear()
        st.rerun()

# 5. FASE GIRONI
if st.session_state['phase'] == "Gironi":
    t1, t2 = st.tabs(["Partite", "Classifica"])
    with t1:
        st.subheader("Risultati del Girone")
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"Match: {m['A']} vs {m['B']}"):
                    c1, c2, c3 = st.columns(3)
                    with c2: st.number_input(f"Set 1 - {m['A'][:5]}", 0, 30, key=f"s1a{idx}")
                    with c3: st.number_input(f"Set 1 - {m['B'][:5]}", 0, 30, key=f"s1b{idx}")
                    ris_finale = st.selectbox("Risultato Set", ["2-0", "2-1", "1-2", "0-2"], key=f"sel{idx}")
                    if st.button("Salva Risultato", key=f"btn{idx}"):
                        v_a, v_b = map(int, ris_finale.split("-"))
                        st.session_state['matches'][idx].update({"SA": v_a, "SB": v_b, "Fatto": True})
                        st.rerun()
    with t2:
        punti = {t: 0 for t in st.session_state['teams']}
        set_v = {t: 0 for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                set_v[m['A']] += m['SA']; set_v[m['B']] += m['SB']
                if m['SA'] > m['SB']: punti[m['A']] += 3
                elif m['SB'] > m['SA']: punti[m['B']] += 3
        df = pd.DataFrame([{"Team": t, "Punti": punti[t], "Set V": set_v[t]} for t in st.session_state['teams']]).sort_values(by=["Punti", "Set V"], ascending=False)
        st.table(df)
        if all(m['Fatto'] for m in st.session_state['matches']):
            st.success("Tutti i match sono conclusi!")
            if st.button("🏆 PROCEDI ALLA FASE AD ELIMINAZIONE"):
                top4 = df["Team"].tolist()[:4]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top4[0], "B": top4[3], "V": None},
                    {"N": "Semi 2", "A": top4[1], "B": top4[2], "V": None}
                ]
                st.session_state['phase'] = "Playoff"
                st.rerun()

# 6. FASE ELIMINAZIONE DIRETTA
elif st.session_state['phase'] == "Playoff":
    st.header("🔥 TABELLONE AD ELIMINAZIONE DIRETTA")
    

[Image of single elimination tournament bracket]

    
    col1, col2 = st.columns(2)
    for i in range(2):
        with [col1, col2][i]:
            p = st.session_state['playoffs'][i]
            st.subheader(p['N'])
            win = st.selectbox(f"Chi vince {p['N']}?", ["-", p['A'], p['B']], key=f"plwin{i}")
            if win != "-": st.session_state['playoffs'][i]['V'] = win

    if all(p.get('V') for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("GENERA FINALISSIMA"):
            st.session_state['playoffs'].append({"N": "FINALE", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.divider()
        f = st.session_state['playoffs'][2]
        st.header(f"🏆 {f['N']}: {f['A']} VS {f['B']}")
        campione = st.selectbox("VINCITORE TROFEO:", ["-", f['A'], f['B']], key="f_winner")
        if campione != "-":
            st.balloons()
            st.success(f"🎊 {campione} CAMPIONE ZERO SKILLS CUP! 🎊")

elif st.session_state['phase'] == "Setup":
    st.info("Configura il torneo e iscrivi i team nella sidebar.")
