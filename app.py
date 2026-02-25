import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. SETUP PAGINA
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

# Funzione per i suoni (Audio Base64 o URL)
def play_sound(sound_type):
    sounds = {
        "click": "https://www.soundjay.com/buttons/button-16.mp3",
        "whistle": "https://www.soundjay.com/human/referee-whistle-01.mp3",
        "win": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    }
    st.components.v1.html(
        f"""
        <audio autoplay>
            <source src="{sounds[sound_type]}" type="audio/mpeg">
        </audio>
        """,
        height=0,
    )

# CSS Avanzato per Bracket e UI
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* Stile Bracket */
    .bracket-container { display: flex; justify-content: space-around; align-items: center; padding: 20px; background: #111; border-radius: 15px; border: 1px solid #4B0082; }
    .bracket-match { border: 2px solid #9370DB; padding: 10px; margin: 10px; border-radius: 8px; min-width: 150px; text-align: center; background: #1a1a1a; }
    .winner-highlight { border-color: #00ff00 !important; box-shadow: 0 0 10px #00ff00; }
    
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { background-color: #9370DB; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'tournament_type' not in st.session_state: st.session_state['tournament_type'] = "Gironi + Eliminazione"

# 3. HEADER
st.title("🏐 ZERO SKILLS CUP")

# 4. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configurazione")
    if st.session_state['phase'] == "Setup":
        st.session_state['tournament_type'] = st.radio("Tipologia:", ["Gironi + Eliminazione", "Solo Eliminazione Diretta"])
        with st.form("form_iscrizione", clear_on_submit=True):
            t_name = st.text_input("Nome Squadra")
            p1 = st.text_input("Giocatore 1")
            p2 = st.text_input("Giocatore 2")
            if st.form_submit_button("Aggiungi Team"):
                if t_name and p1 and p2:
                    entry = f"{t_name} ({p1}/{p2})"
                    if entry not in st.session_state['teams']:
                        st.session_state['teams'].append(entry)
                        play_sound("click")
                        st.rerun()

    st.write("---")
    if st.button("🗑️ RESET TOTALE"):
        st.session_state.clear()
        st.rerun()

# 5. FASE GIRONI
if st.session_state['phase'] == "Gironi":
    t1, t2 = st.tabs(["🎾 Partite", "📈 Classifica"])
    
    with t1:
        # Match da giocare
        st.subheader("Match da disputare")
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"🔥 {m['A']} VS {m['B']}"):
                    ris_finale = st.selectbox("Risultato Set", ["2-0", "2-1", "1-2", "0-2"], key=f"sel{idx}")
                    if st.button("Conferma Risultato", key=f"btn{idx}"):
                        v_a, v_b = map(int, ris_finale.split("-"))
                        st.session_state['matches'][idx].update({"SA": v_a, "SB": v_b, "Fatto": True})
                        play_sound("whistle")
                        st.rerun()

        # Match conclusi (Modificabili)
        st.write("---")
        st.subheader("Match Conclusi (Clicca per modificare)")
        for idx, m in enumerate(st.session_state['matches']):
            if m['Fatto']:
                c1, c2 = st.columns([4, 1])
                c1.info(f"✅ {m['A']} {m['SA']} - {m['SB']} {m['B']}")
                if c2.button("✏️", key=f"mod{idx}"):
                    st.session_state['matches'][idx]['Fatto'] = False
                    st.rerun()

    with t2:
        # Logica Classifica
        punti = {t: 0 for t in st.session_state['teams']}
        set_v = {t: 0 for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                set_v[m['A']] += m['SA']; set_v[m['B']] += m['SB']
                if m['SA'] > m['SB']: punti[m['A']] += 3
                elif m['SB'] > m['SA']: punti[m['B']] += 3
        
        df = pd.DataFrame([{"Team": t, "Punti": punti[t], "Set V": set_v[t]} for t in st.session_state['teams']]).sort_values(by=["Punti", "Set V"], ascending=False)
        st.table(df)
        
        if all(m['Fatto'] for m in st.session_state['matches']) and len(st.session_state['matches']) > 0:
            if st.button("🏆 PROCEDI AI PLAYOFF"):
                top4 = df["Team"].tolist()[:4]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top4[0], "B": top4[3], "V": None},
                    {"N": "Semi 2", "A": top4[1], "B": top4[2], "V": None}
                ]
                st.session_state['phase'] = "Playoff"
                play_sound("whistle")
                st.rerun()

# 6. FASE PLAYOFF (Con Bracket)
elif st.session_state['phase'] == "Playoff":
    st.header("🔥 TABELLONE FINALE")
    
    # Visualizzazione Bracket
    st.markdown("### Bracket")
    b1, b2, b3 = st.columns([1, 0.5, 1])
    
    with b1: # Semifinali
        for i in range(2):
            p = st.session_state['playoffs'][i]
            style = "winner-highlight" if p['V'] else ""
            st.markdown(f"""<div class="bracket-match {style}">{p['A']}<br>vs<br>{p['B']}</div>""", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", p['A'], p['B']], key=f"plwin{i}")
            if win != "-" and st.session_state['playoffs'][i]['V'] != win:
                st.session_state['playoffs'][i]['V'] = win
                play_sound("click")
                st.rerun()

    with b2: # Connessione visiva
        st.write("➡️")
        if len(st.session_state['playoffs']) > 2:
            st.write("🏆")

    with b3: # Finale
        if all(p.get('V') for p in st.session_state['playoffs'][:2]):
            if len(st.session_state['playoffs']) == 2:
                if st.button("Genera Finale"):
                    st.session_state['playoffs'].append({"N": "FINALE", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
                    st.rerun()
            
            if len(st.session_state['playoffs']) > 2:
                f = st.session_state['playoffs'][2]
                st.markdown(f"""<div class="bracket-match" style="border-color: gold;">{f['A']}<br>vs<br>{f['B']}</div>""", unsafe_allow_html=True)
                campione = st.selectbox("CAMPIONE:", ["-", f['A'], f['B']], key="f_winner")
                if campione != "-":
                    st.balloons()
                    play_sound("win")
                    st.success(f"🎊 {campione} CAMPIONE! 🎊")

elif st.session_state['phase'] == "Setup":
    st.info("Iscrivi i team per iniziare.")
    if len(st.session_state['teams']) >= 4:
        if st.button("🚀 INIZIA"):
            # Logica avvio (Gironi o Playoff) come nel codice precedente
            if st.session_state['tournament_type'] == "Gironi + Eliminazione":
                st.session_state['phase'] = "Gironi"
                lista = st.session_state['teams']
                for i in range(len(lista)):
                    for j in range(i + 1, len(lista)):
                        st.session_state['matches'].append({"A": lista[i], "B": lista[j], "SA": 0, "SB": 0, "Fatto": False})
            else:
                st.session_state['phase'] = "Playoff"
                top4 = st.session_state['teams'][:4]
                st.session_state['playoffs'] = [{"N": "Semi 1", "A": top4[0], "B": top4[3], "V": None},{"N": "Semi 2", "A": top4[1], "B": top4[2], "V": None}]
            play_sound("whistle")
            st.rerun()
