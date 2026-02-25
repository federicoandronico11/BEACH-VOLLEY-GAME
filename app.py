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

# CSS Avanzato
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; text-align: center; }
    
    /* Counter Styling */
    .counter-container {
        background: #111;
        border: 2px solid #9370DB;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .counter-number { font-size: 3rem; font-weight: bold; color: #00ff00; }
    .counter-label { font-size: 1rem; color: #aaa; text-transform: uppercase; }

    .bracket-box {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 2px solid #4B0082;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(147, 112, 219, 0.3);
    }
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'use_points' not in st.session_state: st.session_state['use_points'] = False
if 'min_teams' not in st.session_state: st.session_state['min_teams'] = 4

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    if st.session_state['phase'] == "Setup":
        # COUNTER E SOGLIA MINIMA
        num_iscritti = len(st.session_state['teams'])
        st.markdown(f"""
            <div class="counter-container">
                <div class="counter-label">Squadre Iscritte</div>
                <div class="counter-number">{num_iscritti}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state['min_teams'] = st.number_input("Soglia minima per iniziare:", min_value=4, step=2, value=st.session_state['min_teams'])
        
        st.write("---")
        st.session_state['use_points'] = st.toggle("Abilita Quoziente Punti", value=st.session_state['use_points'])
        
        with st.form("iscrizione", clear_on_submit=True):
            t_name = st.text_input("Nome Team")
            p1 = st.text_input("Player 1")
            p2 = st.text_input("Player 2")
            if st.form_submit_button("Iscrivi"):
                if t_name and p1 and p2:
                    st.session_state['teams'].append(f"{t_name} ({p1}/{p2})")
                    play_sound("click")
                    st.rerun()
    
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
                    p_a, p_b = 0, 0
                    if st.session_state['use_points']:
                        c1, c2 = st.columns(2)
                        p_a = c1.number_input(f"Punti {m['A'][:5]}", 0, 100, key=f"pa{idx}")
                        p_b = c2.number_input(f"Punti {m['B'][:5]}", 0, 100, key=f"pb{idx}")
                    
                    ris = st.selectbox("Risultato Set", ["2-0", "2-1", "1-2", "0-2"], key=f"sel{idx}")
                    if st.button("Invia", key=f"go{idx}"):
                        v_a, v_b = map(int, ris.split("-"))
                        st.session_state['matches'][idx].update({"SA": v_a, "SB": v_b, "PA": p_a, "PB": p_b, "Fatto": True})
                        play_sound("whistle")
                        st.rerun()

        with st.expander("✏️ Modifica match conclusi"):
            for idx, m in enumerate(st.session_state['matches']):
                if m['Fatto']:
                    if st.button(f"Ripristina {m['A']} vs {m['B']}", key=f"mod{idx}"):
                        st.session_state['matches'][idx]['Fatto'] = False
                        st.rerun()

    with t2:
        res = {t: {"Punti": 0, "Set V": 0, "PF": 0, "PS": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']]["Set V"] += m['SA']; res[m['B']]["Set V"] += m['SB']
                res[m['A']]["PF"] += m.get('PA', 0); res[m['B']]["PF"] += m.get('PB', 0)
                res[m['A']]["PS"] += m.get('PB', 0); res[m['B']]["PS"] += m.get('PA', 0)
                if m['SA'] > m['SB']: res[m['A']]["Punti"] += 3
                else: res[m['B']]["Punti"] += 3
        
        df = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df['Diff'] = df['PF'] - df['PS']
        df = df.sort_values(by=["Punti", "Set V", "Diff"], ascending=False)
        st.table(df)

        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 PASSA AI PLAYOFF"):
                top = df["index"].tolist()[:4]
                st.session_state['playoffs'] = [{"N": "Semi 1", "A": top[0], "B": top[3], "V": None, "L": None},
                                                {"N": "Semi 2", "A": top[1], "B": top[2], "V": None, "L": None}]
                st.session_state['phase'] = "Playoff"
                st.rerun()

# 5. PLAYOFF & FINALI
elif st.session_state['phase'] == "Playoff":
    st.header("🏁 FASE FINALE")
    
    col_s1, col_s2 = st.columns(2)
    for i in range(2):
        with [col_s1, col_s2][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'><div>{p['A']}</div><div style='color:#9370DB'>VS</div><div>{p['B']}</div></div>", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", p['A'], p['B']], key=f"win{i}")
            if win != "-":
                st.session_state['playoffs'][i]['V'] = win
                st.session_state['playoffs'][i]['L'] = p['B'] if win == p['A'] else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALISSIMA", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3° POSTO", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.divider()
        c_fin, c_34 = st.columns(2)
        with c_fin:
            f = st.session_state['playoffs'][2]
            st.subheader("🥇 FINALE 1° POSTO")
            st.markdown(f"<div class='bracket-box' style='border-color:gold;'>{f['A']} VS {f['B']}</div>", unsafe_allow_html=True)
            campione = st.selectbox("CAMPIONE:", ["-", f['A'], f['B']], key="gold")
            if campione != "-":
                st.balloons(); play_sound("win")
                st.success(f"🏆 {campione} CAMPIONE!")
        with c_34:
            f3 = st.session_state['playoffs'][3]
            st.subheader("🥉 FINALE 3° POSTO")
            st.markdown(f"<div class='bracket-box' style='border-color:#cd7f32;'>{f3['A']} VS {f3['B']}</div>", unsafe_allow_html=True)
            st.selectbox("3° CLASSIFICATO:", ["-", f3['A'], f3['B']], key="bronze")

# 6. SETUP INIZIALE
elif st.session_state['phase'] == "Setup":
    st.info(f"Raggiungi {st.session_state['min_teams']} squadre per iniziare.")
    if len(st.session_state['teams']) >= st.session_state['min_teams']:
        if st.button("🚀 INIZIA ZERO SKILLS CUP"):
            st.session_state['phase'] = "Gironi"
            lt = st.session_state['teams']
            for i in range(len(lt)):
                for j in range(i+1, len(lt)):
                    st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "PA": 0, "PB": 0, "Fatto": False})
            play_sound("whistle")
            st.rerun()
