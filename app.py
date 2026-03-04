import streamlit as st
import time
import engine # Isso importa as funções do arquivo acima

st.set_page_config(page_title="AURAXIS V15 PRO", layout="wide")

# Inicialização do Histórico
if 'historico' not in st.session_state:
    st.session_state.historico = {
        "SCALPER": {"wins": 0, "losses": 0, "trade_ativo": None},
        "DAY": {"wins": 0, "losses": 0, "trade_ativo": None},
        "SWING": {"wins": 0, "losses": 0, "trade_ativo": None}
    }

placeholder = st.empty()

while True:
    with placeholder.container():
        df, pips = engine.obter_dados_institucionais()
        tendencia, _ = engine.detectar_tendencia_macro()
        
        if not df.empty:
            p_atual = float(df['close'].iloc[-1])
            st.metric("EUR/USD MT5 SYNC", f"{p_atual:.5f}", f"{pips:.1f} Pips")
            
            cols = st.columns(3)
            for i, perfil in enumerate(["SCALPER", "DAY", "SWING"]):
                with cols[i]:
                    dados = engine.motor_auraxis_v15(df, perfil)
                    stats = st.session_state.historico[perfil]
                    
                    # Lógica de Auditoria
                    if stats['trade_ativo']:
                        res = engine.verificar_desfecho(p_atual, stats['trade_ativo'])
                        if res:
                            st.session_state.historico[perfil][res.lower() + "s"] += 1
                            st.session_state.historico[perfil]['trade_ativo'] = None
                    
                    if dados['tipo'] and not stats['trade_ativo']:
                        st.session_state.historico[perfil]['trade_ativo'] = dados
                    
                    st.write(f"### {perfil}")
                    st.write(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
                    if dados['tipo']: st.success(f"Sinal: {dados['tipo']}")
        
        time.sleep(30)
