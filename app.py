import streamlit as st
import time
from engine import obter_dados_institucionais, motor_auraxis_v15
from interface import configurar_layout, exibir_modulo

# Configuração inicial da página
st.set_page_config(page_title="AURAXIS V15", layout="wide")
configurar_layout()

# Espaço reservado para atualização em tempo real
container_principal = st.empty()

while True:
    with container_principal.container():
        df, pips = obter_dados_institucionais()
        
        if not df.empty:
            preco_atual = float(df['close'].iloc[-1])
            cor_pips = "#3fb950" if pips >= 0 else "#f85149"
            
            # Cabeçalho de Preço
            st.markdown(f"""
                <div style='text-align:center; padding:20px;'>
                    <h1 style='font-size:3.5rem; margin:0;'>{preco_atual:.5f}</h1>
                    <b style='color:{cor_pips}; font-size:1.2rem;'>{"▲" if pips>=0 else "▼"} {abs(pips):.1f} PIPS HOJE</b>
                </div>
            """, unsafe_allow_html=True)
            
            # Colunas de Perfis
            col1, col2, col3, col4 = st.columns(4)
            perfis = ["SCALPER", "DAY TRADE", "SWING", "POSITION"]
            colunas = [col1, col2, col3, col4]
            
            for perfil, col in zip(perfis, colunas):
                with col:
                    # O nome do perfil vai para o motor sem o espaço
                    dados = motor_auraxis_v15(df, perfil.split()[0])
                    exibir_modulo(perfil, dados)
            
            st.caption("⚙️ Auraxis Sentinel V15 | Motor Estatístico Ativo | Atualização: 5s")
        else:
            st.warning("Conectando ao terminal de liquidez...")
            
    time.sleep(5)
