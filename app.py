import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. SETUP PAGINA
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

# Funzione Audio
def play_sound(sound_type):
    sounds = {
        "click": "https://www.soundjay.com/buttons/button-16.mp3",
        "whistle": "https://www.soundjay.com/human/referee-whistle-01.mp3",
        "win": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    }
    components.html(f"<audio autoplay><source src='{sounds[sound_type]}' type='audio/mpeg'></audio>", height=0)

# CSS Avanzato per Bracket e Grafica
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; text-align: center; }
    
    /* Bracket Design */
    .bracket-box {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 2px solid #4B0082;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(147, 112, 219, 0.3);
    }
    .bracket-team { font-weight: bold; font-size: 1.1rem; color: #ffffff; }
    .vs-text { color: #9370DB; font-size: 0.8rem; margin: 5px 0; }
    .winner-glow { border-color: #00ff00 !important; box-shadow: 0 0 20px rgba(0, 255, 0, 0.4); }
    
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'use_points' not in st.session_state: st.session_state['use_points'] = False

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ Impostazioni")
    if st.session_state['phase'] == "Setup":
        st.session_state['use_points'] = st.toggle("Abilita Quoziente Punti (Set singoli)", value=False)
        st.write("---")
        with st.form("iscrizione", clear_on_submit=True):
            t_name = st.text_input("Nome Team")
            p1 = st.text_input("Player 1")
            p2 = st.text_input("Player 2")
            if st.form_submit_button("Iscrivi"):
                if t_name and p1 and p2:
                    st.session_state['teams'].append(f"{t_name} ({p1}/{p2})")
                    play_sound("click")
                    st.rerun()
    
    st.write(f"Iscritti: {len(st.session_state['teams'])}")
    if st.button("🗑️ RESET"):
        st.session_state.clear()
        st.rerun()

# 4. LOGICA GIRONI
if st.session_state['phase'] == "Gironi":
    t1, t2 = st.tabs(["🎾 Match Day", "📈 Classifica"])
    
    with t1:
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"🏟️ {m['A']} vs {m['B']}"):
                    # Se l'utente ha attivato i punti set
                    p_a, p_b = 0, 0
                    if st.session_state['use_points']:
                        c1, c2 = st.columns(2)
                        p_a = c1.number_input(f"Punti Totali {m['A'][:5]}", 0, 100, key=f"pa{idx}")
                        p_b = c2.number_input(f"Punti Totali {m['B'][:5]}", 0, 100, key=f"pb{idx}")
                    
                    ris = st.selectbox("Risultato Set", ["2-0", "2-1", "1-2", "0-2"], key=f"sel{idx}")
                    if st.button("Invia", key=f"go{idx}"):
                        v_a, v_b = map(int, ris.split("-"))
                        st.session_state['matches'][idx].update({
                            "SA": v_a, "SB": v_b, "PA": p_a, "PB": p_b, "Fatto": True
                        })
                        play_sound("whistle")
                        st.rerun()
            else:
                st.info(f"✅ {m['A']} {m['SA']} - {m['SB']} {m['B']} (Modifica in basso)")

        if any(m['Fatto'] for m in st.session_state['matches']):
            with st.expander("✏️ Modifica match conclusi"):
                for idx, m in enumerate(st.session_state['matches']):
                    if m['Fatto']:
                        if st.button(f"Ripristina {m['A']} vs {m['B']}", key=f"mod{idx}"):
                            st.session_state['matches'][idx]['Fatto'] = False
                            st.rerun()

    with t2:
        res = {t: {"Punti": 0, "Set V": 0, "Punti Fatti": 0, "Punti Subiti": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Done' if 'Done' in m else 'Fatto']:
                res[m['A']]["Set V"] += m['SA']
                res[m['B']]["Set V"] += m['SB']
                res[m['A']]["Punti Fatti"] += m.get('PA', 0)
                res[m['B']]["Punti Fatti"] += m.get('PB', 0)
                res[m['A']]["Punti Subiti"] += m.get('PB', 0)
                res[m['B']]["Punti Subiti"] += m.get('PA', 0)
                if m['SA'] > m['SB']: res[m['A']]["Punti"] += 3
                else: res[m['B']]["Punti"] += 3
        
        df = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df['Diff Punti'] = df['Punti Fatti'] - df['Punti Subiti']
        df = df.sort_values(by=["Punti", "Set V", "Diff Punti"], ascending=False)
        st.table(df)

        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 PASSA AI PLAYOFF"):
                top = df["index"].tolist()[:4]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top[0], "B": top[3], "V": None, "L": None},
                    {"N": "Semi 2", "A": top[1], "B": top[2], "V": None, "L": None}
                ]
                st.session_state['phase'] = "Playoff"
                st.rerun()

# 5. FASE PLAYOFF (Bracket Migliorato)
elif st.session_state['phase'] == "Playoff":
    st.header("🏁 TABELLONE ELIMINAZIONE DIRETTA")
    
    
    
    # Visualizzazione Semifinali
    col_s1, col_s2 = st.columns(2)
    for i in range(2):
        with [col_s1, col_s2][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'><div class='bracket-team'>{p['A']}</div><div class='vs-text'>VS</div><div class='bracket-team'>{p['B']}</div></div>", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", p['A'], p['B']], key=f"win{i}")
            if win != "-":
                st.session_state['playoffs'][i]['V'] = win
                st.session_state['playoffs'][i]['L'] = p['B'] if win == p['A'] else p['A']

    # Generazione Finali (1/2 e 3/4)
    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            # Finale 1°/2° posto
            st.session_state['playoffs'].append({"N": "FINALISSIMA", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            # Finale 3°/4° posto
            st.session_state['playoffs'].append({"N": "FINALE 3°/4° POSTO", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.divider()
        c_fin, c_34 = st.columns(2)
        
        with c_fin:
            f = st.session_state['playoffs'][2]
            st.subheader("🥇 FINALE 1° POSTO")
            st.markdown(f"<div class='bracket-box' style='border-color:gold;'><div class='bracket-team'>{f['A']}</div><div class='vs-text'>VS</div><div class='bracket-team'>{f['B']}</div></div>", unsafe_allow_html=True)
            campione = st.selectbox("CAMPIONE:", ["-", f['A'], f['B']], key="gold")
            if campione != "-":
                st.balloons()
                play_sound("win")
                st.success(f"🏆 {campione} CAMPIONE!")

        with c_34:
            f3 = st.session_state['playoffs'][3]
            st.subheader("🥉 FINALE 3° POSTO")
            st.markdown(f"<div class='bracket-box' style='border-color:bronze;'><div class='bracket-team'>{f3['A']}</div><div class='vs-text'>VS</div><div class='bracket-team'>{f3['B']}</div></div>", unsafe_allow_html=True)
            terzo = st.selectbox("3° CLASSIFICATO:", ["-", f3['A'], f3['B']], key="bronze")

# 6. SETUP INIZIALE
elif st.session_state['phase'] == "Setup":
    st.info("Configura il torneo e iscrivi almeno 4 squadre.")
    if len(st.session_state['teams']) >= 4:
        if st.button("🚀 INIZIA ZERO SKILLS CUP"):
            st.session_state['phase'] = "Gironi"
            st.session_state['matches'] = []
            lt = st.session_state['teams']
            for i in range(len(lt)):
                for j in range(i+1, len(lt)):
                    st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "PA": 0, "PB": 0, "Fatto": False})
            play_sound("whistle")
            st.rerun()
