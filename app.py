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
    
    .mega-counter {
        background: linear-gradient(180deg, #111, #000);
        border: 3px solid #9370DB;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }
    .counter-val { font-size: 5rem; font-weight: 900; color: #00ff00; line-height: 1; }
    .counter-sub { font-size: 1.2rem; color: #9370DB; text-transform: uppercase; }

    .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .paid { background-color: #00ff00; box-shadow: 0 0 8px #00ff00; }
    .not-paid { background-color: #ff0000; box-shadow: 0 0 8px #ff0000; }

    .ranking-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #222; font-family: 'Courier New', monospace; }
    .bracket-box { background: #111; border: 2px solid #4B0082; border-radius: 15px; padding: 20px; text-align: center; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE DATABASE (Persistenza nella sessione)
if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {} 
if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []

# Variabili Torneo
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
if 'min_teams' not in st.session_state: st.session_state['min_teams'] = 4

# 3. PANNELLO SINISTRO (RANKING LIVE & EXPORT)
with st.sidebar:
    st.title("📊 LIVE RANKING")
    
    if not st.session_state['ranking_atleti']:
        st.info("Nessun atleta nel ranking.")
    else:
        # Ordina e visualizza Ranking Live
        sorted_rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
        for i, (name, pts) in enumerate(sorted_rank):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏐"
            st.markdown(f"<div class='ranking-row'><span>{medal} {name}</span><span style='color:#00ff00'>{pts}</span></div>", unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🖼️ EXPORT RANKING GRAFICO"):
            rows = "".join([f"<tr><td style='padding:10px; font-size:24px;'>{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else '🏐'} {n}</td><td style='padding:10px; font-size:24px; font-weight:bold;'>{p} PT</td></tr>" for i, (n, p) in enumerate(sorted_rank)])
            html_ranking = f"<div style='background: linear-gradient(135deg, #4B0082, #9370DB); padding: 40px; border-radius: 20px; color: white; text-align: center; font-family: sans-serif;'><h1 style='font-size: 40px;'>🏆 ZERO SKILLS RANKING</h1><table style='width: 100%; margin-top: 20px;'>{rows}</table></div>"
            st.components.v1.html(html_ranking, height=500, scrolling=True)

    st.write("---")
    with st.expander("🏅 Albo d'Oro"):
        for win in st.session_state['albo_oro']: st.write(win)

    if st.button("🗑️ RESET TOTALE"):
        st.session_state.clear()
        st.rerun()

# 4. SCHERMATA SETUP
if st.session_state['phase'] == "Setup":
    st.markdown(f"""<div class="mega-counter"><div class="counter-val">{len(st.session_state['teams'])}</div><div class="counter-sub">Squadre Iscritte</div></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Iscrizione Team")
        with st.form("iscrizione", clear_on_submit=True):
            # Selezione o Inserimento Team
            t_name_opt = st.selectbox("Seleziona Team esistente", ["-"] + sorted(list(set(st.session_state['db_teams']))))
            t_name_new = st.text_input("Oppure nuovo Nome Squadra")
            t_name = t_name_new if t_name_new else t_name_opt
            
            # Selezione o Inserimento Atleti
            st.write("**Atleta 1**")
            p1_opt = st.selectbox("Cerca nel DB", ["-"] + sorted(st.session_state['db_atleti']), key="p1_sel")
            p1_new = st.text_input("Oppure Nome e Cognome nuovo Atleta 1")
            p1 = p1_new if p1_new else p1_opt

            st.write("**Atleta 2**")
            p2_opt = st.selectbox("Cerca nel DB", ["-"] + sorted(st.session_state['db_atleti']), key="p2_sel")
            p2_new = st.text_input("Oppure Nome e Cognome nuovo Atleta 2")
            p2 = p2_new if p2_new else p2_opt

            paid = st.checkbox("Quota pagata")
            
            if st.form_submit_button("Conferma Iscrizione"):
                if t_name != "-" and p1 != "-" and p2 != "-":
                    st.session_state['teams'].append({"full": f"{t_name} ({p1}/{p2})", "name": t_name, "p1": p1, "p2": p2, "paid": paid})
                    # Aggiornamento Database
                    if t_name not in st.session_state['db_teams']: st.session_state['db_teams'].append(t_name)
                    for p in [p1, p2]:
                        if p not in st.session_state['db_atleti']: 
                            st.session_state['db_atleti'].append(p)
                            st.session_state['ranking_atleti'][p] = 0
                    play_sound("click")
                    st.rerun()

    with col2:
        st.subheader("Check-in")
        for t in st.session_state['teams']:
            status = "paid" if t['paid'] else "not-paid"
            st.markdown(f"<div><span class='status-dot {status}'></span> {t['full']}</div>", unsafe_allow_html=True)
        
        st.write("---")
        st.session_state['min_teams'] = st.number_input("Minimo per iniziare:", 4, 32, value=st.session_state['min_teams'])
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO"):
                st.session_state['phase'] = "Gironi"
                lt = st.session_state['teams']
                for i in range(len(lt)):
                    for j in range(i+1, len(lt)):
                        st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False})
                play_sound("whistle"); st.rerun()

# 5. FASE GIRONI
elif st.session_state['phase'] == "Gironi":
    st.header("🎾 GIRONI QUALIFICAZIONE")
    t1, t2 = st.tabs(["Calendario", "Classifica Live"])
    with t1:
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"Match: {m['A']['name']} vs {m['B']['name']}"):
                    ris = st.selectbox("Risultato", ["2-0", "2-1", "1-2", "0-2"], key=f"r{idx}")
                    if st.button("Salva", key=f"c{idx}"):
                        v_a, v_b = map(int, ris.split("-"))
                        st.session_state['matches'][idx].update({"SA": v_a, "SB": v_b, "Fatto": True})
                        play_sound("click"); st.rerun()
    with t2:
        res = {t['full']: {"P": 0, "S": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']['full']]["S"] += m['SA']; res[m['B']['full']]["S"] += m['SB']
                if m['SA'] > m['SB']: res[m['A']['full']]["P"] += 3
                else: res[m['B']['full']]["P"] += 3
        df = pd.DataFrame.from_dict(res, orient='index').reset_index().sort_values(by=["P", "S"], ascending=False)
        st.table(df)
        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 PASSA AI PLAYOFF"):
                top = df["index"].tolist()[:4]
                top_teams = [next(t for t in st.session_state['teams'] if t['full'] == name) for name in top]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top_teams[0], "B": top_teams[3], "V": None, "L": None},
                    {"N": "Semi 2", "A": top_teams[1], "B": top_teams[2], "V": None, "L": None}
                ]
                st.session_state['phase'] = "Playoff"; st.rerun()

# 6. FASE PLAYOFF
elif st.session_state['phase'] == "Playoff":
    st.header("🔥 FINAL FOUR")
    c1, c2 = st.columns(2)
    for i in range(2):
        with [c1, c2][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'>{p['A']['name']}<br>vs<br>{p['B']['name']}</div>", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", "Team A", "Team B"], key=f"p{i}")
            if win != "-":
                st.session_state['playoffs'][i]['V'] = p['A'] if win == "Team A" else p['B']
                st.session_state['playoffs'][i]['L'] = p['B'] if win == "Team A" else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3°", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        f1 = st.session_state['playoffs'][2]
        st.markdown(f"<div class='bracket-box' style='border-color:gold;'>ORO: {f1['A']['name']} vs {f1['B']['name']}</div>", unsafe_allow_html=True)
        winner_choice = st.selectbox("CAMPIONE:", ["-", f1['A']['name'], f1['B']['name']], key="final")
        
        if winner_choice != "-" and st.button("🏁 CHIUDI E ASSEGNA PUNTI"):
            vincitore = f1['A'] if winner_choice == f1['A']['name'] else f1['B']
            pts = len(st.session_state['teams']) * 10
            st.session_state['ranking_atleti'][vincitore['p1']] += pts
            st.session_state['ranking_atleti'][vincitore['p2']] += pts
            st.session_state['albo_oro'].append(f"🏆 {vincitore['name']} ({vincitore['p1']}/{vincitore['p2']})")
            st.balloons(); play_sound("win")
            st.session_state['phase'] = "Setup"; st.session_state['teams'] = []; st.rerun()
