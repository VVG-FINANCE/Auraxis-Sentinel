import streamlit as st
import time
from engine import obter_dados_institucionais, motor_auraxis_v15
from interface import configurar_layout, exibir_modulo

st.set_page_config(page_title="AURAXIS V15 SOBERANO", layout="wide")
configurar_layout()

# Espaço de atualização dinâmica
cockpit = st.empty()

while True:
    with cockpit.container():
        df, pips = obter_dados_institucionais()
        
        if not df.empty:
            preco = float(df['close'].iloc[-1])
            cor_v = "#3fb950" if pips >= 0 else "#f85149"
            
            # HUD Superior de Impacto
            st.markdown(f"""
                <div style="text-align:center; background:#0d1117; padding:25px; border-radius:15px; border-bottom: 4px solid #58a6ff;">
                    <h1 style="font-size:4.5rem; margin:0; letter-spacing:-2px;">{preco:.5f}</h1>
                    <b style="color:{cor_v}; font-size:1.3rem;">{"▲" if pips>=0 else "▼"} {abs(pips):.1f} PIPS HOJE</b>
                </div>
                <br>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            perfis = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            espacos = [col1, col2, col3, col4]
            
            for p, col in zip(perfis, espacos):
                with col:
                    dados_m = motor_auraxis_v15(df, p.split()[0])
                    # Limpeza automática se o preço romper a zona de proteção
                    if dados_m['tipo'] and not (dados_m['z_inf'] <= preco <= dados_m['z_sup']):
                        dados_m['tipo'] = None
                    exibir_modulo(p, dados_m)
            
            st.caption("⚙️ MOTOR NEURAL V15: Z-Score Adaptativo + Amostragem Fractal + Biometria de Candle")
        else:
            st.warning("⚠️ Aguardando conexão com os servidores de liquidez...")
            
    time.sleep(5)
