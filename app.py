import streamlit as st
import time
from engine import obter_dados_institucionais, motor_auraxis_v15
from interface import configurar_layout, exibir_modulo

st.set_page_config(page_title="AURAXIS V15", layout="wide")
configurar_layout()
cockpit = st.empty()

while True:
    with cockpit.container():
        df, pips = obter_dados_institucionais()
        if not df.empty:
            preco = float(df['close'].iloc[-1])
            st.markdown(f"<div style='text-align:center;'><h1>{preco:.5f}</h1><b style='color:{'#3fb950' if pips>=0 else '#f85149'}'>{pips:.1f} PIPS HOJE</b></div>", unsafe_allow_html=True)
            
            cols = st.columns(4)
            perfis = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            for p, col in zip(perfis, cols):
                with col:
                    dados = motor_auraxis_v15(df, p.split()[0])
                    exibir_modulo(p, dados)
        else:
            st.error("Aguardando Fluxo...")
    time.sleep(5)
