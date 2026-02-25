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
    
    /* Indicatori Pagamento */
    .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .paid { background-color: #00ff00; box-shadow: 0 0 8px #00ff00; }
    .not-paid { background-color: #ff0000; box-shadow: 0 0 8px #ff0000; }

    /* Ranking & Albo d'oro UI */
    .info-box { background: #111; border: 1px solid #4B0082; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 0.9rem; }
    .ranking-item { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 5px 0; }
    
    .bracket-box { background: linear-gradient(145deg, #1a1a1a, #0d0d0d); border: 2px solid #4B0082; border-radius: 15px; padding: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE DATABASE PERSISTENTE (Simulato in session_state)
if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
if 'db_players' not in st.session_state: st.session_state['db_players'] = []
if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
if 'ranking' not in st.session_state: st.session_state['ranking'] = {} # {Nome: Punti}

# Variabili Torneo Corrente
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'min_teams' not in st.session_state: st.session_state['min_teams'] = 4

# 3. SIDEBAR: RANKING E ALBO D'ORO (Sempre visibili)
with st.sidebar:
    st.title("📊 STATISTICHE")
    
    with st.expander("🏆 ALBO D'ORO", expanded=True):
        if not st.session_state['albo_oro']:
            st.write("Nessun torneo concluso.")
        for win in st.session_state['albo_oro']:
            st.write(f"🥇 {win}")

    with st.expander("📈 RANKING ZERO SKILLS", expanded=True):
        if not st.session_state['ranking']:
            st.write("Nessun punto assegnato.")
        else:
            sorted_rank = sorted(st.session_state['ranking'].items(), key=lambda x: x[1], reverse=True)
            for name, pts in sorted_rank:
                st.markdown(f"<div class='ranking-item'><span>{name}</span><span style='color:#00ff00'>{pts} pt</span></div>", unsafe_allow_html=True)

    st.write("---")
    if st.button("🗑️ RESET APP"):
        st.session_state.clear()
        st.rerun()

# 4. SCHERMATA SETUP / ISCRIZIONI
if st.session_state['phase'] == "Setup":
    st.header("📝 ISCRIZIONI E CONFIGURAZIONE")
    
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("Nuovo Team")
        with st.form("iscrizione", clear_on_submit=True):
            # Autocomplete simulato tramite lista precaricata (selectbox con opzione vuota o text_input con datalist)
            t_name = st.selectbox("Cerca o scrivi Team", [""] + sorted(list(set(st.session_state['db_teams']))), placeholder="Seleziona Team...", index=0)
            if t_name == "": t_name = st.text_input("Oppure nuovo Nome Team")
            
            p1 = st.text_input("Giocatore 1 (Nome)")
            p2 = st.text_input("Giocatore 2 (Nome)")
            quota = st.checkbox("Quota Iscrizione Versata (€)")
            
            if st.form_submit_button("Conferma Iscrizione"):
                if t_name and p1 and p2:
                    team_entry = {
                        "full_name": f"{t_name} ({p1}/{p2})",
                        "name": t_name,
                        "p1": p1, "p2": p2,
                        "paid": quota
                    }
                    st.session_state['teams'].append(team_entry)
                    # Salvataggio nel database globale
                    st.session_state['db_teams'].append(t_name)
                    st.session_state['db_players'].extend([p1, p2])
                    play_sound("click")
                    st.rerun()

    with col_r:
        st.subheader("Lista Iscritti")
        for t in st.session_state['teams']:
            dot_class = "paid" if t['paid'] else "not-paid"
            st.markdown(f"<div><span class='status-dot {dot_class}'></span>{t['full_name']}</div>", unsafe_allow_html=True)
        
        st.write(f"**Totale: {len(st.session_state['teams'])} / Minimo: {st.session_state['min_teams']}**")
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO"):
                st.session_state['phase'] = "Gironi"
                st.session_state['matches'] = []
                lt = st.session_state['teams']
                for i in range(len(lt)):
                    for j in range(i+1, len(lt)):
                        st.session_state['matches'].append({"A": lt[i]['full_name'], "B": lt[j]['full_name'], "SA": 0, "SB": 0, "Fatto": False})
                play_sound("whistle")
                st.rerun()

# 5. FASE GIRONI
elif st.session_state['phase'] == "Gironi":
    st.header("🎾 FASE A GIRONI")
    t1, t2 = st.tabs(["Match", "Classifica"])
    
    with t1:
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"🏟️ {m['A']} vs {m['B']}"):
                    ris = st.selectbox("Risultato Set", ["2-0", "2-1", "1-2", "0-2"], key=f"sel{idx}")
                    if st.button("Salva", key=f"go{idx}"):
                        v_a, v_b = map(int, ris.split("-"))
                        st.session_state['matches'][idx].update({"SA": v_a, "SB": v_b, "Fatto": True})
                        play_sound("click")
                        st.rerun()
    
    with t2:
        # Logica classifica semplificata (Punti e Set)
        scores = {t['full_name']: {"P": 0, "S": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                scores[m['A']]["S"] += m['SA']; scores[m['B']]["S"] += m['SB']
                if m['SA'] > m['SB']: scores[m['A']]["P"] += 3
                else: scores[m['B']]["P"] += 3
        
        df = pd.DataFrame.from_dict(scores, orient='index').reset_index().sort_values(by=["P", "S"], ascending=False)
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

# 6. FASE PLAYOFF E ASSEGNAZIONE PUNTI RANKING
elif st.session_state['phase'] == "Playoff":
    st.header("🏁 FINAL FOUR")
    
    # 
    
    col1, col2 = st.columns(2)
    for i in range(2):
        with [col1, col2][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'>{p['A']}<br>VS<br>{p['B']}</div>", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", p['A'], p['B']], key=f"w{i}")
            if win != "-":
                st.session_state['playoffs'][i]['V'] = win
                st.session_state['playoffs'][i]['L'] = p['B'] if win == p['A'] else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3°", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        f1 = st.session_state['playoffs'][2]
        st.markdown(f"<div class='bracket-box' style='border-color:gold;'>FINALE: {f1['A']} vs {f1['B']}</div>", unsafe_allow_html=True)
        campione = st.selectbox("CAMPIONE:", ["-", f1['A'], f1['B']], key="gold")
        
        if campione != "-" and st.button("🏁 CHIUDI TORNEO E ASSEGNA RANKING"):
            # 1. Albo d'oro
            st.session_state['albo_oro'].append(campione)
            
            # 2. Calcolo Punti Ranking (Esempio: 10 pt * numero coppie al primo, e a scalare)
            num_coppie = len(st.session_state['teams'])
            punti_base = num_coppie * 10
            
            # Assegnazione semplificata (chiunque ha partecipato riceve qualcosa, i finalisti di più)
            # In una versione reale, useremmo la classifica finale completa
            if campione not in st.session_state['ranking']: st.session_state['ranking'][campione] = 0
            st.session_state['ranking'][campione] += punti_base
            
            st.balloons()
            play_sound("win")
            st.session_state['phase'] = "Setup"
            st.session_state['teams'] = [] # Svuota per il prossimo torneo
            st.rerun()
