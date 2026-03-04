import streamlit as st
import time
import engine

st.set_page_config(page_title="AURAXIS V15 PRO - AUDIT", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA ---
if 'historico' not in st.session_state:
    st.session_state.historico = {
        "SCALPER": {"wins": 0, "losses": 0, "trade_ativo": None},
        "DAY": {"wins": 0, "losses": 0, "trade_ativo": None},
        "SWING": {"wins": 0, "losses": 0, "trade_ativo": None}
    }

# Estilização do Placar
st.markdown("""
<style>
    .stat-card { background: #0d1117; border: 1px dashed #30363d; padding: 10px; border-radius: 5px; text-align: center; }
    .win-text { color: #238636; font-weight: bold; }
    .loss-text { color: #da3633; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

while True:
    with placeholder.container():
        df, pips = engine.obter_dados_institucionais()
        tendencia, _ = engine.detectar_tendencia_macro()
        
        if not df.empty:
            p_atual = df['close'].iloc[-1]
            
            # --- TOPO: PREÇO E TENDÊNCIA ---
            c1, c2 = st.columns([2, 1])
            c1.metric("EUR/USD MT5", f"{p_atual:.5f}", f"{pips:.1f} Pips")
            c2.subheader(f"Macro: {tendencia}")

            st.divider()

            # --- CORPO: CARDS OPERACIONAIS ---
            cols = st.columns(3)
            perfis_nomes = ["SCALPER", "DAY", "SWING"]

            for i, perfil in enumerate(perfis_nomes):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    stats = st.session_state.historico[perfil]
                    
                    st.write(f"### {perfil}")
                    st.progress(dados['score']/100)

                    # LÓGICA DE REGISTRO E MONITORAMENTO
                    # 1. Se não há trade ativo e surge um sinal, abre o trade
                    if stats['trade_ativo'] is None and dados['tipo'] is not None:
                        st.session_state.historico[perfil]['trade_ativo'] = dados
                        st.info(f"🚀 Nova {dados['tipo']} Iniciada")
                    
                    # 2. Se há trade ativo, monitora o desfecho
                    elif stats['trade_ativo'] is not None:
                        t_ativo = stats['trade_ativo']
                        resultado = engine.verificar_desfecho(p_atual, t_ativo)
                        
                        if resultado == "WIN":
                            st.session_state.historico[perfil]['wins'] += 1
                            st.session_state.historico[perfil]['trade_ativo'] = None
                            st.balloons()
                        elif resultado == "LOSS":
                            st.session_state.historico[perfil]['losses'] += 1
                            st.session_state.historico[perfil]['trade_ativo'] = None

                        # Exibe o trade que está sendo monitorado no momento
                        st.warning(f"Monitorando: {t_ativo['tipo']} (TP: {t_ativo['tp1']:.5f})")

                    # Exibição do sinal atual do motor (visual apenas)
                    if dados['tipo']:
                        cor = "green" if dados['tipo'] == "COMPRA" else "red"
                        st.markdown(f"#### :{cor}[SINAL: {dados['tipo']}]")
                        st.caption(f"TP: {dados['tp1']:.5f} | SL: {dados['sl']:.5f}")
                    else:
                        st.write("Aguardando Gatilho...")

            # --- RODAPÉ: PLACAR FIXO E TAXA DE ACERTO ---
            st.divider()
            st.markdown("### 📈 PERFORMANCE REAL (Eficácia do Motor)")
            foot_cols = st.columns(3)
            
            for i, perfil in enumerate(perfis_nomes):
                with foot_cols[i]:
                    h = st.session_state.historico[perfil]
                    total = h['wins'] + h['losses']
                    taxa = (h['wins'] / total * 100) if total > 0 else 0
                    
                    st.markdown(f"""
                    <div class="stat-card">
                        <b>{perfil}</b><br>
                        <span class="win-text">WINS: {h['wins']}</span> | 
                        <span class="loss-text">LOSS: {h['losses']}</span><br>
                        <small>Taxa de Acerto: {taxa:.1f}%</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.error("Erro de Conexão...")

    time.sleep(30)
    st.cache_data.clear()
