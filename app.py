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

# Memória do Robô
if 'audit' not in st.session_state:
    st.session_state.audit = {p: {"wins": 0, "losses": 0, "ativo": None} for p in ["SCALPER", "DAY", "SWING"]}

def main():
    df, pips = engine.obter_dados_institucionais()
    tendencia = engine.detectar_tendencia_macro()

    if not df.empty:
        p_atual = float(df['close'].iloc[-1])
        
        # HEADER (Imagem 1000011847/48)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.metric("EUR/USD MT5 SYNC (-30)", f"{p_atual:.5f}", f"{pips:.1f} Pips Hoje")
        with c2:
            st.markdown(f"**TENDÊNCIA GLOBAL (H4)**")
            cor = "#238636" if "ALTA" in tendencia else "#da3633"
            st.markdown(f"<h2 style='color:{cor};'>{tendencia}</h2>", unsafe_allow_html=True)

        st.divider()

        # CARDS (Híbrido Imagem 1000011843 e 1000011842)
        cols = st.columns(3)
        for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
            with cols[i]:
                dados = engine.motor_auraxis_v15(df, perfil)
                db = st.session_state.audit[perfil]

                # Auditoria em tempo real
                if db['ativo']:
                    resultado = engine.verificar_desfecho(p_atual, db['ativo'])
                    if resultado:
                        st.session_state.audit[perfil][resultado.lower() + "s"] += 1
                        st.session_state.audit[perfil]['ativo'] = None
                        st.balloons() if resultado == "WIN" else st.snow()

                st.subheader(perfil)
                st.write(f"Prontidão: {dados['score']:.1f}%")
                st.progress(dados['score']/100)

                if dados['tipo']:
                    if not db['ativo']: st.session_state.audit[perfil]['ativo'] = dados
                    cor_s = "#238636" if dados['tipo'] == "COMPRA" else "#da3633"
                    st.markdown(f"<h3 style='color:{cor_s};'>{dados['tipo']} ATIVA</h3>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="signal-card">
                        <small>ZONA DE ENTRADA</small><br>
                        <b>{dados['z_inf']:.5f} — {dados['z_sup']:.5f}</b><br><br>
                        <div style="display:flex; justify-content:space-between;">
                            <span>TP: <b style="color:#238636;">{dados['tp1']:.5f}</b></span>
                            <span>SL: <b style="color:#da3633;">{dados['sl']:.5f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Aguardando Alinhamento...")

        # RODAPÉ DE EFICÁCIA (Sua solicitação de contador fixo)
        st.divider()
        st.write("### 📊 AUDITORIA DE PERFORMANCE")
        f1, f2, f3 = st.columns(3)
        for col, p in zip([f1, f2, f3], ["SCALPER", "DAY", "SWING"]):
            h = st.session_state.audit[p]
            total = h['wins'] + h['losses']
            taxa = (h['wins']/total*100) if total > 0 else 0
            col.markdown(f"""
            <div class="metric-card">
                <b>{p}</b><br>
                <span class="win-box">WINS: {h['wins']}</span> | <span class="loss-box">LOSS: {h['losses']}</span><br>
                <small>Taxa: {taxa:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    time.sleep(30)
    st.rerun() # Forma correta de atualizar sem dar erro 503
