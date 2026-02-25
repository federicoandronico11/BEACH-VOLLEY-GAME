import streamlit as st
import pandas as pd

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; }
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE SICURA
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"

# 3. HEADER
st.title("ZERO SKILLS CUP")
st.write("Se hai 0 skills, sei nel posto giusto")

# 4. SIDEBAR - GESTIONE TEAM CON FORM (Previene errori di invio)
with st.sidebar:
    st.header("Iscrizioni")
    
    if st.session_state['phase'] == "Setup":
        with st.form("form_iscrizione", clear_on_submit=True):
            t_name = st.text_input("Nome Squadra")
            p1 = st.text_input("Giocatore 1")
            p2 = st.text_input("Giocatore 2")
            submit_team = st.form_submit_button("Aggiungi Team")
            
            if submit_team:
                if t_name and p1 and p2:
                    entry = f"{t_name} ({p1}/{p2})"
                    if entry not in st.session_state['teams']:
                        st.session_state['teams'].append(entry)
                        st.success(f"Team {t_name} iscritto!")
                    else:
                        st.error("Team già presente!")
                else:
                    st.warning("Riempi tutti i campi!")

    st.write("---")
    st.write(f"Squadre: {len(st.session_state['teams'])}")
    for t in st.session_state['teams']:
        st.text(f"• {t}")

    if len(st.session_state['teams']) >= 4 and st.session_state['phase'] == "Setup":
        if st.button("🚀 AVVIA TORNEO"):
            st.session_state['phase'] = "Gironi"
            st.session_state['matches'] = []
            lista = st.session_state['teams']
            for i in range(len(lista)):
                for j in range(i + 1, len(lista)):
                    st.session_state['matches'].append({
                        "A": lista[i], "B": lista[j], 
                        "SA": 0, "SB": 0, "Fatto": False
                    })
            st.rerun()
            
    if st.button("🗑️ RESET TOTALE"):
        st.session_state.clear()
        st.rerun()

# 5. LOGICA FASE GIRONI
if st.session_state['phase'] == "Gironi":
    t1, t2 = st.tabs(["Partite", "Classifica"])
    
    with t1:
        st.subheader("Inserimento Risultati")
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                c1, c2, c3, c4, c5 = st.columns([3,1,1,3,1])
                c1.write(m['A'])
                sa = c2.number_input("S", 0, 2, key=f"sa{idx}")
                sb = c3.number_input("S", 0, 2, key=f"sb{idx}")
                c4.write(m['B'])
                if c5.button("Invia", key=f"btn{idx}"):
                    st.session_state['matches'][idx]['SA'] = sa
                    st.session_state['matches'][idx]['SB'] = sb
                    st.session_state['matches'][idx]['Fatto'] = True
                    st.rerun()
        
    with t2:
        punti = {t: 0 for t in st.session_state['teams']}
        set_v = {t: 0 for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                set_v[m['A']] += m['SA']
                set_v[m['B']] += m['SB']
                if m['SA'] > m['SB']: punti[m['A']] += 3
                elif m['SB'] > m['SA']: punti[m['B']] += 3
        
        cl_data = [{"Team": t, "Punti": punti[t], "Set V": set_v[t]} for t in st.session_state['teams']]
        df = pd.DataFrame(cl_data).sort_values(by=["Punti", "Set V"], ascending=False)
        st.table(df)

        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 GENERA PLAYOFF"):
                top4 = df["Team"].tolist()[:4]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top4[0], "B": top4[3], "V": None},
                    {"N": "Semi 2", "A": top4[1], "B": top4[2], "V": None}
                ]
                st.session_state['phase'] = "Playoff"
                st.rerun()

# 6. FASE PLAYOFF
elif st.session_state['phase'] == "Playoff":
    st.header("Tabellone Finale")
    
    

[Image of a single elimination tournament bracket]


    for i in range(min(2, len(st.session_state['playoffs']))):
        p = st.session_state['playoffs'][i]
        st.subheader(p['N'])
        win = st.selectbox(f"Vincitore {p['N']}", ["-", p['A'], p['B']], key=f"plwin{i}")
        if win != "-":
            st.session_state['playoffs'][i]['V'] = win

    if len(st.session_state['playoffs']) == 2:
        if all(st.session_state['playoffs'][i]['V'] is not None for i in range(2)):
            if st.button("Crea Finale"):
                st.session_state['playoffs'].append({
                    "N": "FINALE", 
                    "A": st.session_state['playoffs'][0]['V'], 
                    "B": st.session_state['playoffs'][1]['V'], 
                    "V": None
                })
                st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.divider()
        f = st.session_state['playoffs'][2]
        st.header(f"🏆 {f['N']}: {f['A']} VS {f['B']}")
        campione = st.selectbox("CAMPIONE:", ["-", f['A'], f['B']], key="final_winner")
        if campione != "-":
            st.balloons()
            st.success(f"🎊 {campione} CAMPIONE ZERO SKILLS CUP! 🎊")
