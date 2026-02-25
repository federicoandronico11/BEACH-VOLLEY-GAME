import streamlit as st

def load_css():
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
        .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .paid { background-color: #00ff00; }
        .not-paid { background-color: #ff0000; }
        .ranking-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #222; }
        </style>
        """, unsafe_allow_html=True)

def mega_counter(count):
    st.markdown(f"""
        <div class="mega-counter">
            <div class="counter-val">{count}</div>
            <div style="color: #9370DB; text-transform: uppercase;">Squadre Iscritte</div>
        </div>
    """, unsafe_allow_html=True)
