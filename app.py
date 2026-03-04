import streamlit as st
import time
from engine import obter_dados_hifi, motor_neural_v15
from interface import aplicar_estilo_v15, desenhar_radar

st.set_page_config(page_title="AURAXIS V15", layout="wide")
aplicar_estilo_v15()

# Placeholder para atualização em tempo real
espaco_vivo = st.empty()

while True:
    with espaco_vivo.container():
        df, pips = obter_dados_hifi()
        
        if not df.empty:
            preco_atual = float(df['close'].iloc[-1])
            cor_pips = "#3fb950" if pips >= 0 else "#f85149"
            
            # Painel Superior
            st.markdown(f"""
                <div style="text-align:center; background:#0d1117; padding:20px; border-radius:15px; border:1px solid #30363d;">
                    <h1 style="font-size:4rem; margin:0; color:white;">{preco_atual:.5f}</h1>
                    <b style="color:{cor_pips}; font-size:1.2rem;">
                        {"▲" if pips >= 0 else "▼"} {abs(pips):.1f} PIPS HOJE
                    </b>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # Colunas para os 4 Tipos
            col1, col2, col3, col4 = st.columns(4)
            
            tempos = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            cols = [col1, col2, col3, col4]
            
            for t, c in zip(tempos, cols):
                with c:
                    dados = motor_neural_v15(df, t.split()[0])
                    # Lógica de sumir se romper a zona
                    if dados['tipo'] and not (dados['z_inf'] <= preco_atual <= dados['z_sup']):
                        dados['tipo'] = None
                    desenhar_radar(t, dados)
                    
            st.caption("Sistema Auraxis V15 // Leitura Biométrica de Candle // Atualização: 5s")
        else:
            st.error("Conectando ao Fluxo de Dados...")
            
    time.sleep(5)
