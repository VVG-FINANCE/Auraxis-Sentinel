import streamlit as st

def configurar_layout():
    st.markdown("""
        <style>
        .stApp { background-color: #040508; color: #ffffff; }
        .card-auraxis { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 15px; }
        .barra-fundo { background: #161b22; height: 12px; border-radius: 6px; margin: 8px 0; overflow: hidden; }
        .barra-fill { height: 100%; transition: width 0.6s ease; }
        .texto-mini { font-size: 0.65rem; color: #8b949e; font-weight: 700; }
        </style>
    """, unsafe_allow_html=True)

def exibir_modulo(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_corpo = "#3fb950" if direcao > 0 else "#f85149"
    
    st.markdown(f"""
    <div class="card-auraxis">
        <div style="display:flex; justify-content:space-between;">
            <b>{titulo}</b>
            <span style="color:#58a6ff;">PRONTIDÃO: {score:.1f}%</span>
        </div>
        <div style="margin-top:15px;">
            <div class="texto-mini">DIREÇÃO (CORPO)</div>
            <div class="barra-fundo"><div class="barra-fill" style="width:{abs(direcao)}%; background:{cor_corpo};"></div></div>
            <div class="texto-mini">PRESSÃO (PAVIO)</div>
            <div class="barra-fundo"><div class="barra-fill" style="width:{pressao}%; background:#f1e05a;"></div></div>
        </div>
    """, unsafe_allow_html=True)

    if dados['tipo']:
        cor = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
        st.markdown(f"""
            <div style="border: 1px solid {cor}; padding:10px; border-radius:8px; margin-top:10px;">
                <b style="color:{cor};">{dados['tipo']} ATIVA</b><br>
                <div style="display:grid; grid-template-columns: 1fr 1fr; font-size:0.8rem;">
                    <div><small>LUCRO (TP)</small><br>{dados['tp'][0]:.5f}<br>{dados['tp'][1]:.5f}</div>
                    <div><small>RISCO (SL)</small><br>{dados['sl'][0]:.5f}<br>{dados['sl'][1]:.5f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
