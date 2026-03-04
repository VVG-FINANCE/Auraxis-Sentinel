import streamlit as st
import time
import engine

st.set_page_config(page_title="AURAXIS V15 PRO", layout="wide")

# Estilização Pro (Combinação das imagens enviadas)
st.markdown("""
<style>
    .card-full { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; }
    .stat-box { background: #0d1117; border: 1px solid #238636; border-radius: 8px; padding: 15px; text-align: center; }
    .tp-text { color: #238636; font-weight: bold; }
    .sl-text { color: #da3633; font-weight: bold; }
    .score-text { font-size: 0.9rem; color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# Inicialização da Auditoria (Placar Fixo)
if 'audit' not in st.session_state:
    st.session_state.audit = {p: {"wins": 0, "losses": 0, "ativo": None} for p in ["SCALPER", "DAY", "SWING"]}

placeholder = st.empty()

while True:
    with placeholder.container():
        # Coleta centralizada para evitar Rate Limit
        df, pips = engine.obter_dados_institucionais()
        
        if not df.empty:
            tendencia = engine.detectar_tendencia_macro(df)
            p_atual = float(df['close'].iloc[-1])
            
            # Topo Informativo
            c1, c2 = st.columns([2, 1])
            with c1:
                st.metric("EUR/USD (MT5 SYNC -30)", f"{p_atual:.5f}", f"{pips:.1f} Pips Hoje")
            with c2:
                cor_t = "#238636" if "ALTA" in tendencia else "#da3633"
                st.markdown(f"**TENDÊNCIA H4**<br><h2 style='color:{cor_t}; margin:0;'>{tendencia}</h2>", unsafe_allow_html=True)

            st.divider()

            # Grid de Operações
            cols = st.columns(3)
            for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    db = st.session_state.audit[perfil]

                    # Auditoria em Tempo Real
                    if db['ativo']:
                        resultado = engine.verificar_desfecho(p_atual, db['ativo'])
                        if resultado:
                            st.session_state.audit[perfil][resultado.lower() + "s"] += 1
                            st.session_state.audit[perfil]['ativo'] = None
                            if resultado == "WIN": st.balloons()

                    # Interface do Card
                    st.markdown(f"### {perfil}")
                    st.markdown(f"<span class='score-text'>Prontidão: {dados['score']:.1f}%</span>", unsafe_allow_html=True)
                    st.progress(dados['score']/100)

                    if dados['tipo']:
                        if not db['ativo']: st.session_state.audit[perfil]['ativo'] = dados
                        cor_s = "#238636" if dados['tipo'] == "COMPRA" else "#da3633"
                        
                        st.markdown(f"""
                        <div class='card-full'>
                            <h3 style='color:{cor_s}; text-align:center; margin:0;'>{dados['tipo']} ATIVA</h3>
                            <hr style='border: 0.5px solid #30363d;'>
                            <p style='margin:0;'><b>ENTRADA:</b> {p_atual:.5f}</p>
                            <p class='tp-text' style='margin:0;'><b>ALVO (TP):</b> {dados['tp1']:.5f}</p>
                            <p class='sl-text' style='margin:0;'><b>RISCO (SL):</b> {dados['sl']:.5f}</p>
                            <br>
                            <small style='color:#8b949e;'>Z-Score: {dados['z']:.2f}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    elif db['ativo']:
                        st.warning(f"Monitorando {db['ativo']['tipo']} em andamento...")
                    else:
                        st.info("Buscando exaustão institucional...")

            # Rodapé: Placar de Eficácia Verdadeira
            st.divider()
            st.markdown("### 📊 PLACAR DE PERFORMANCE (EFICÁCIA DO MOTOR)")
            f_cols = st.columns(3)
            for j, p in enumerate(["SCALPER", "DAY", "SWING"]):
                h = st.session_state.audit[p]
                total = h['wins'] + h['losses']
                taxa = (h['wins']/total*100) if total > 0 else 0
                
                f_cols[j].markdown(f"""
                <div class='stat-box'>
                    <b>{p}</b><br>
                    <span style='color:#238636;'>WINS: {h['wins']}</span> | 
                    <span style='color:#da3633;'>LOSS: {h['losses']}</span><br>
                    <span style='font-size:1.5rem; font-weight:bold; color:#58a6ff;'>{taxa:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Conexão instável com o Yahoo Finance. Reajustando...")

    time.sleep(45) # Delay maior para evitar o Rate Limit do Yahoo
