import streamlit as st
import time
import engine

st.set_page_config(page_title="AURAXIS V15 PRO", layout="wide")

# Estilos das Zonas e Auditoria
st.markdown("""
<style>
    .card-full { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; }
    .stat-box { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center; }
    .win-text { color: #238636; font-weight: bold; font-size: 1.3rem; }
    .loss-text { color: #da3633; font-weight: bold; font-size: 1.3rem; }
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
            
            # --- DASHBOARD PRINCIPAL ---
            c1, c2 = st.columns([2, 1])
            c1.metric("EUR/USD (MT5 ADJUSTED)", f"{p_atual:.5f}", f"{pips:.1f} Pips Hoje")
            cor_t = "#238636" if "ALTA" in tendencia else "#da3633"
            c2.markdown(f"**MACRO BIAS**<br><h2 style='color:{cor_t}; margin:0;'>{tendencia}</h2>", unsafe_allow_html=True)

            st.divider()

            cols = st.columns(3)
            for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    db = st.session_state.audit[perfil]

                    # Auditoria Fixa
                    if db['ativo']:
                        res = engine.verificar_desfecho(p_atual, db['ativo'])
                        if res:
                            st.session_state.audit[perfil][res.lower() + "s"] += 1
                            st.session_state.audit[perfil]['ativo'] = None
                            if res == "WIN": st.balloons()

                    st.subheader(perfil)
                    st.progress(dados['score']/100)

                    if dados['tipo']:
                        if not db['ativo']: st.session_state.audit[perfil]['ativo'] = dados
                        cor = "#238636" if dados['tipo'] == "COMPRA" else "#da3633"
                        st.markdown(f"""
                        <div class='card-full'>
                            <h3 style='color:{cor};'>{dados['tipo']}</h3>
                            <b>TP: {dados['tp1']:.5f}</b><br>
                            <b>SL: {dados['sl']:.5f}</b>
                        </div>
                        """, unsafe_allow_html=True)
                    elif db['ativo']:
                        st.warning(f"Trade em curso...")
                    else:
                        st.info("Varrendo Zonas...")

            # --- PLACAR FIXO NO FINAL DA TELA ---
            st.divider()
            st.markdown("### 🏆 AUDITORIA DE EFICÁCIA (TOTAL ACUMULADO)")
            f_cols = st.columns(3)
            for j, p in enumerate(["SCALPER", "DAY", "SWING"]):
                h = st.session_state.audit[p]
                total = h['wins'] + h['losses']
                taxa = (h['wins']/total*100) if total > 0 else 0
                f_cols[j].markdown(f"""
                <div class='stat-box'>
                    <b>{p}</b><br>
                    <span class='win-text'>W: {h['wins']}</span> | <span class='loss-text'>L: {h['losses']}</span><br>
                    <span style='color:#58a6ff; font-size:1.2rem;'>Taxa: {taxa:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Aguardando liberação da API Yahoo...")

    time.sleep(60) # Intervalo seguro contra bloqueios
