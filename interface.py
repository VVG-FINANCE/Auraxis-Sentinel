import streamlit as st

def configurar_layout():
    st.markdown("""
        <style>
        .stApp { background-color: #040508; color: #ffffff; }
        .card-auraxis { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 15px; }
        .barra-fundo { background: #161b22; height: 10px; border-radius: 5px; margin: 8px 0; overflow: hidden; }
        .barra-fill { height: 100%; transition: width 0.6s ease; }
        .texto-mini { font-size: 0.65rem; color: #8b949e; font-weight: 700; text-transform: uppercase; }
        </style>
    """, unsafe_allow_html=True)

def exibir_modulo(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_direcao = "#3fb950" if direcao > 0 else "#f85149"
    
    html = f"""
    <div class="card-auraxis">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="font-size:1rem;">{titulo}</b>
            <span style="color:#58a6ff; font-family:monospace;">PRONTIDÃO: {score:.1f}%</span>
        </div>
        <div style="margin-top:12px;">
            <div class="texto-mini">Direção (Corpo)</div>
            <div class="barra-fundo"><div class="barra-fill" style="width:{min(abs(direcao), 100)}%; background:{cor_direcao};"></div></div>
            <div class="texto-mini">Pressão (Pavio/Rejeição)</div>
            <div class="barra-fundo"><div class="barra-fill" style="width:{min(pressao, 100)}%; background:#f1e05a;"></div></div>
        </div>
    """

    if dados['tipo']:
        cor_sinal = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
        html += f"""
        <div style="border-top:1px solid #30363d; margin-top:12px; padding-top:12px;">
            <b style="color:{cor_sinal};">{dados['tipo']} ATIVA</b><br>
            <div style="display:grid; grid-template-columns: 1fr 1fr; font-size:0.8rem; margin-top:8px;">
                <div><small style="color:#8b949e;">LUCRO (TP)</small><br><b>{dados['tp'][0]:.5f}</b></div>
                <div><small style="color:#8b949e;">RISCO (SL)</small><br><b>{dados['sl'][0]:.5f}</b></div>
            </div>
        </div>
        """
    else:
        html += '<div style="text-align:center; color:#30363d; font-size:0.7rem; margin-top:12px;">AGUARDANDO FLUXO...</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
