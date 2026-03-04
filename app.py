import streamlit as st
import time
from engine import obter_dados_institucionais, motor_auraxis_v15
from interface import configurar_tema, exibir_radar

st.set_page_config(page_title="AURAXIS V15", layout="wide")
configurar_tema()
cockpit = st.empty()

while True:
    with cockpit.container():
        df, pips = obter_dados_institucionais()
        if not df.empty:
            preco = float(df['close'].iloc[-1])
            cor_v = "#3fb950" if pips >= 0 else "#f85149"
            
            st.markdown(f"""
                <div style="text-align:center; background:#0d1117; padding:25px; border-radius:15px;">
                    <h1 style="font-size:4rem; margin:0;">{preco:.5f}</h1>
                    <b style="color:{cor_v}; font-size:1.3rem;">{"▲" if pips>=0 else "▼"} {abs(pips):.1f} PIPS HOJE</b>
                </div><br>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            modos = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            for m, c in zip(modos, col1, col2, col3, col4):
                with c:
                    dados_m = motor_auraxis_v15(df, m.split()[0])
                    exibir_radar(m, dados_m)
        else:
            st.error("Conectando ao fluxo de liquidez...")
    time.sleep(5)
