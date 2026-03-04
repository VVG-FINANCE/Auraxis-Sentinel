import streamlit as st
import time
import engine

st.set_page_config(page_title="AURAXIS V15 PRO", layout="wide")

# CSS para o visual híbrido das imagens
st.markdown("""
<style>
    .metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center; }
    .signal-card { background: #0d1117; border-left: 5px solid #58a6ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .win-box { color: #238636; font-weight: bold; font-size: 1.2rem; }
    .loss-box { color: #da3633; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

if 'audit' not in st.session_state:
    st.session_state.audit = {p: {"wins": 0, "losses": 0, "ativo": None} for p in ["SCALPER", "DAY", "SWING"]}

placeholder = st.empty()

# Loop Principal Otimizado
while True:
    with placeholder.container():
        # Única chamada de dados por ciclo
        df, pips = engine.obter_dados_institucionais()
        
        if not df.empty:
            tendencia = engine.detectar_tendencia_macro(df)
            p_atual = float(df['close'].iloc[-1])
            
            # Interface de Cabeçalho
            c1, c2 = st.columns([2, 1])
            c1.metric("EUR/USD MT5 SYNC (-30)", f"{p_atual:.5f}", f"{pips:.1f} Pips Hoje")
            cor_t = "#238636" if "ALTA" in tendencia else "#da3633"
            c2.markdown(f"**TENDÊNCIA MACRO**<br><h2 style='color:{cor_t}; margin:0;'>{tendencia}</h2>", unsafe_allow_html=True)

            st.divider()

            # Processamento por Perfil
            cols = st.columns(3)
            for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    db = st.session_state.audit[perfil]

                    # Auditoria de Trades Ativos
                    if db['ativo']:
                        # Compara o preço ajustado atual com o alvo guardado
                        res_audit = engine.verificar_desfecho(p_atual, db['ativo'])
                        if res_audit:
                            st.session_state.audit[perfil][res_audit.lower() + "s"] += 1
                            st.session_state.audit[perfil]['ativo'] = None
                            if res_audit == "WIN": st.balloons()

                    st.subheader(perfil)
                    st.write(f"Prontidão: {dados['score']:.1f}%")
                    st.progress(dados['score']/100)

                    if dados['tipo']:
                        if not db['ativo']: st.session_state.audit[perfil]['ativo'] = dados
                        cor_s = "#238636" if dados['tipo'] == "COMPRA" else "#da3633"
                        st.markdown(f"<h3 style='color:{cor_s};'>{dados['tipo']} ATIVA</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                            <div class="signal-card">
                                <small>ALVOS DA ZONA</small><br>
                                TP: <b style="color:#238636;">{dados['tp1']:.5f}</b><br>
                                SL: <b style="color:#da3633;">{dados['sl']:.5f}</b>
                            </div>
                        """, unsafe_allow_html=True)
                    elif db['ativo']:
                        st.warning(f"Monitorando {db['ativo']['tipo']}...")
                    else:
                        st.info("🔍 Varrendo Liquidez...")

            # Painel de Auditoria Fixo
            st.divider()
            st.write("### 📊 PLACAR DE EFICÁCIA (ESTATÍSTICA REAL)")
            f1, f2, f3 = st.columns(3)
            for col, p in zip([f1, f2, f3], ["SCALPER", "DAY", "SWING"]):
                h = st.session_state.audit[p]
                total = h['wins'] + h['losses']
                taxa = (h['wins']/total*100) if total > 0 else 0
                col.markdown(f"""
                <div class="metric-card">
                    <b>{p}</b><br>
                    <span class="win-box">WINS: {h['wins']}</span> | <span class="loss-box">LOSS: {h['losses']}</span><br>
                    <span style="font-size:1.4rem; color:#58a6ff;">{taxa:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Rate Limit do Yahoo detectado. Aguardando 60 segundos para tentar novamente...")
            time.sleep(60)

    time.sleep(30)
