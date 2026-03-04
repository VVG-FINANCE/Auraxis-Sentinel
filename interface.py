import streamlit as st

def configurar_layout():
    st.markdown("""
        <style>
        .stApp { background-color: #040508; color: #ffffff; font-family: 'Inter', sans-serif; }
        .card-auraxis { 
            background: #0d1117; border: 1px solid #30363d; border-radius: 12px; 
            padding: 18px; margin-bottom: 15px; position: relative;
        }
        .barra-fundo { background: #161b22; height: 12px; border-radius: 6px; margin: 8px 0; overflow: hidden; }
        .barra-fill { height: 100%; transition: width 0.6s ease; }
        .texto-identificador { font-size: 0.65rem; color: #8b949e; letter-spacing: 1px; font-weight: 700; }
        .alerta-operacao { padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def exibir_modulo(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_corpo = "#3fb950" if direcao > 0 else "#f85149"
    
    with st.container():
        # HTML encapsulado para garantir visualização e não código
        st.markdown(f"""
        <div class="card-auraxis">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:1.1rem;">{titulo}</b>
                <span style="color:#58a6ff; font-family:monospace; font-size:0.9rem;">PRONTIDÃO: {score:.1f}%</span>
            </div>
            
            <div style="margin-top:15px;">
                <div class="texto-identificador">DIREÇÃO (CORPO DO CANDLE)</div>
                <div class="barra-fundo">
                    <div class="barra-fill" style="width:{min(abs(direcao), 100)}%; background:{cor_corpo};"></div>
                </div>
                
                <div class="texto-identificador">PRESSÃO (PAVIO/ABSORÇÃO)</div>
                <div class="barra-fundo">
                    <div class="barra-fill" style="width:{min(pressao, 100)}%; background:#f1e05a;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if dados['tipo']:
            cor = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
            st.markdown(f"""
                <div class="alerta-operacao" style="border: 1px solid {cor}; background: {cor}15;">
                    <b style="color:{cor}; font-size:1.2rem;">{dados['tipo']} ATIVA</b><br>
                    <code style="color:#58a6ff;">ZONA: {dados['z_inf']:.5f} — {dados['z_sup']:.5f}</code>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; margin-top:10px; text-align:left;">
                        <div><small style="color:#3fb950;">ALVOS (TP)</small><br><b>{dados['tp'][0]:.5f}</b><br><b>{dados['tp'][1]:.5f}</b></div>
                        <div><small style="color:#f85149;">RISCOS (SL)</small><br><b>{dados['sl'][0]:.5f}</b><br><b>{dados['sl'][1]:.5f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:15px; color:#30363d; font-size:0.75rem;'>VARREDURA DE LIQUIDEZ ATIVA...</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
