import streamlit as st

def configurar_tema():
    st.markdown("""
        <style>
        .stApp { background-color: #05070a; color: #ffffff; }
        .bloco-card { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
        .barra-fundo { background: #161b22; height: 12px; border-radius: 6px; margin: 10px 0; overflow: hidden; }
        .barra-corpo { height: 100%; transition: width 0.6s ease; }
        .barra-pavio { height: 100%; background: #f1e05a; }
        .texto-id { font-size: 0.7rem; color: #8b949e; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

def exibir_radar(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_d = "#3fb950" if direcao > 0 else "#f85149"
    
    # Construção HTML
    html = f"""
    <div class="bloco-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="font-size:1.1rem;">{titulo}</b>
            <span style="color:#58a6ff;">PRONTIDÃO: {score:.1f}%</span>
        </div>
        <div style="margin-top:15px;">
            <div class="texto-id">DIREÇÃO (CORPO)</div>
            <div class="barra-fundo"><div class="barra-corpo" style="width:{min(abs(direcao), 100)}%; background:{cor_d};"></div></div>
            <div class="texto-id">PRESSÃO (PAVIO)</div>
            <div class="barra-fundo"><div class="barra-corpo barra-pavio" style="width:{min(pressao, 100)}%;"></div></div>
        </div>
    """

    if dados['tipo']:
        cor_t = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
        html += f"""
        <div style="border-top: 1px solid #30363d; margin-top:15px; padding-top:15px;">
            <b style="color:{cor_t}; font-size:1.2rem;">{dados['tipo']} ATIVA</b><br>
            <code style="color:#58a6ff;">ZONA: {dados['z_inf']:.5f} — {dados['z_sup']:.5f}</code>
            <div style="display:grid; grid-template-columns: 1fr 1fr; margin-top:10px;">
                <div><small style="color:#3fb950;">ALVOS (TP)</small><br><b>{dados['tp'][0]:.5f}</b></div>
                <div><small style="color:#f85149;">RISCO (SL)</small><br><b>{dados['sl'][0]:.5f}</b></div>
            </div>
        </div>
        """
    else:
        html += '<div style="text-align:center; color:#333; font-size:0.7rem; margin-top:15px;">VARREDURA ATIVA...</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
