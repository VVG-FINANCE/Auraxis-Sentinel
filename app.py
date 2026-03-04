import streamlit as st
import time
import engine

st.set_page_config(page_title="AURAXIS SENTINEL V15", layout="wide")

# CSS para interface híbrida (Imagens de Cards + Placar)
st.markdown("""
<style>
    .main-card { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
    .audit-box { background: #161b22; border-top: 4px solid #58a6ff; padding: 15px; border-radius: 0 0 10px 10px; text-align: center; }
    .win { color: #238636; font-weight: bold; }
    .loss { color: #da3633; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'audit' not in st.session_state:
    st.session_state.audit = {p: {"wins": 0, "losses": 0, "ativo": None} for p in ["SCALPER", "DAY", "SWING"]}

placeholder = st.empty()

while True:
    with placeholder.container():
        df, pips = engine.obter_dados_institucionais()
        
        if not df.empty:
            tendencia = engine.detectar_tendencia_macro(df)
            p_atual = float(df['close'].iloc[-1])
            
            # Header Informativo
            c1, c2 = st.columns([2, 1])
            c1.metric("EUR/USD SYNC MT5", f"{p_atual:.5f}", f"{pips:.1f} Pips")
            c2.subheader(f"BIAS: {tendencia}")

            st.divider()

            # Processamento de Sinais e Auditoria
            cols = st.columns(3)
            for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    
                    # Logica de Auditoria
                    if st.session_state.audit[perfil]['ativo']:
                        resultado = engine.verificar_desfecho(p_atual, st.session_state.audit[perfil]['ativo'])
                        if resultado:
                            st.session_state.audit[perfil][resultado.lower() + "s"] += 1
                            st.session_state.audit[perfil]['ativo'] = None
                            if resultado == "WIN": st.balloons()

                    # Interface de Visualização
                    st.write(f"### {perfil}")
                    st.progress(dados['score']/100)
                    
                    if dados['tipo']:
                        if not st.session_state.audit[perfil]['ativo']:
                            st.session_state.audit[perfil]['ativo'] = dados
                        
                        cor = "#238636" if dados['tipo'] == "COMPRA" else "#da3633"
                        st.markdown(f"<div class='main-card'><h2 style='color:{cor};'>{dados['tipo']}</h2>"
                                    f"<b>TP: {dados['tp1']:.5f}</b><br><b>SL: {dados['sl']:.5f}</b></div>", unsafe_allow_html=True)
                    else:
                        st.info("Monitorando Zonas de Liquidez...")

            # Rodapé de Eficácia Acumulada
            st.divider()
            st.markdown("### 🏆 PERFORMANCE AUDITADA (REAL-TIME)")
            f_cols = st.columns(3)
            for j, p in enumerate(["SCALPER", "DAY", "SWING"]):
                h = st.session_state.audit[p]
                total = h['wins'] + h['losses']
                taxa = (h['wins']/total*100) if total > 0 else 0
                f_cols[j].markdown(f"<div class='audit-box'><b>{p}</b><br>"
                                   f"<span class='win'>W: {h['wins']}</span> | <span class='loss'>L: {h['losses']}</span><br>"
                                   f"Eficácia: {taxa:.1f}%</div>", unsafe_allow_html=True)
        else:
            st.warning("Aguardando resposta do servidor de dados (Yahoo Finance)...")

    time.sleep(60) # Intervalo de segurança anti-bloqueio
