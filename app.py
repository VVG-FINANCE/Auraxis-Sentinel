import streamlit as st
import time
import engine # Importa o arquivo engine.py

st.set_page_config(page_title="AURAXIS V15 PRO", layout="wide")

# CSS para interface limpa
st.markdown("""<style> 
    .stProgress > div > div > div > div { background-color: #58a6ff; }
    .status-box { padding: 15px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

st.title("🛡️ AURAXIS SENTINEL V15 PRO")

# Espaço reservado para o loop de atualização
placeholder = st.empty()

while True:
    with placeholder.container():
        df, pips = engine.obter_dados_institucionais()
        tendencia, forca = engine.detectar_tendencia_macro()
        
        if not df.empty:
            p_atual = float(df['close'].iloc[-1])
            
            # Linha de Informações Macro
            c1, c2, c3 = st.columns([1, 1, 1])
            c1.metric("PREÇO EUR/USD", f"{p_atual:.5f}", f"{pips:.1f} Pips")
            
            with c2:
                cor_t = "#238636" if "ALTA" in tendencia else "#da3633" if "BAIXA" in tendencia else "#ffffff"
                st.markdown(f"""<div class='status-box'>
                    <small>TENDÊNCIA GLOBAL (H4)</small><br>
                    <b style='color:{cor_t}; font-size:1.1rem;'>{tendencia}</b>
                </div>""", unsafe_allow_html=True)
            
            c3.write(f"🕒 **Sincronismo:** {time.strftime('%H:%M:%S')} UTC")
            c3.caption(f"Sessão: {'LONDRES/NY' if 8 <= time.gmtime().tm_hour <= 17 else 'ÁSIA/FECHAMENTO'}")

            st.divider()
            
            # Painel de Perfis Operacionais
            cols = st.columns(4)
            perfis = ["SCALPER", "DAY", "SWING", "POSITION"]
            
            for i, perfil in enumerate(perfis):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    st.subheader(perfil)
                    st.write(f"Prontidão: {dados['score']:.1f}%")
                    st.progress(dados['score'] / 100)
                    
                    if dados['tipo']:
                        cor_s = "green" if dados['tipo'] == "COMPRA" else "red"
                        st.markdown(f"### :{cor_s}[{dados['tipo']} ATIVA]")
                        
                        # Alerta de Confluência com a Macro
                        if (dados['tipo'] == "COMPRA" and "ALTA" in tendencia) or (dados['tipo'] == "VENDA" and "BAIXA" in tendencia):
                            st.success("🔥 ALTA CONVICÇÃO")
                        
                        with st.expander("DETALHES DA ORDEM", expanded=True):
                            st.write(f"**TP:** {dados['tp']:.5f}")
                            st.write(f"**SL:** {dados['sl']:.5f}")
                            st.caption(f"Z-Score: {dados['z']:.2f}")
                    else:
                        st.info("Varredura de Liquidez...")
                        st.caption(f"Direção: {dados['direcao']:.1f}%")
        else:
            st.error("Conectando à API...")
            
    time.sleep(15)
