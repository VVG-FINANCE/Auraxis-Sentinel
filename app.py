import streamlit as st
import time
from engine import obter_dados_institucionais, motor_auraxis_v15
from interface import aplicar_estilo_soberano, renderizar_painel

st.set_page_config(page_title="AURAXIS SOBERANO", layout="wide")
aplicar_estilo_soberano()

placeholder = st.empty()

while True:
    with placeholder.container():
        df, pips = obter_dados_institucionais()
        
        if not df.empty:
            preco = float(df['close'].iloc[-1])
            cor_p = "#3fb950" if pips >= 0 else "#f85149"
            
            # Painel Superior Traduzido
            st.markdown(f"""
                <div style="text-align:center; padding:30px; background:#0d1117; border-radius:15px; border-bottom: 5px solid #58a6ff;">
                    <h1 style="font-size:4.5rem; margin:0;">{preco:.5f}</h1>
                    <b style="color:{cor_p}; font-size:1.4rem;">{"▲" if pips>=0 else "▼"} {abs(pips):.1f} PIPS HOJE</b>
                </div>
                <br>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            modos = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            colunas = [c1, c2, c3, c4]
            
            for m, col in zip(modos, colunas):
                with col:
                    dados = motor_auraxis_v15(df, m.split()[0])
                    # Lógica para limpar sinal se o preço sair da zona
                    if dados['tipo'] and not (dados['z_inf'] <= preco <= dados['z_sup']):
                        dados['tipo'] = None
                    renderizar_painel(m, dados)
            
            st.caption("⚙️ MOTOR V15: Musculatura Neural Ativa // Ciclo 5s // Tradução Nativa")
        else:
            st.error("Conectando ao fluxo de dados...")
            
    time.sleep(5)
