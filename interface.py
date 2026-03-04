import streamlit as st

def aplicar_estilo_soberano():
    st.markdown("""
        <style>
        .stApp { background-color: #05070a; color: #ffffff; }
        .bloco-card { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
        .barra-fundo { background: #161b22; height: 12px; border-radius: 6px; margin: 10px 0; overflow: hidden; }
        .barra-corpo { height: 100%; transition: width 0.6s ease; }
        .barra-pavio { height: 100%; background: #f1e05a; transition: width 0.6s ease; }
        .label-bio { font-size: 0.7rem; color: #8b949e; font-weight: bold; text-transform: uppercase; }
        </style>
    """, unsafe_allow_html=True)

def renderizar_painel(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_direcao = "#3fb950" if direcao > 0 else "#f85149"
    
    # Este bloco constrói a visualização que você verá na tela
    html_painel = f"""
    <div class="bloco-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="font-size:1.1rem;">{titulo}</b>
            <span style="color:#58a6ff; font-family:monospace;">PRONTIDÃO: {score:.1f}%</span>
        </div>
        
        <div style="margin-top:15px;">
            <div class="label-bio">Direção (Força do Corpo)</div>
            <div class="barra-fundo">
                <div class="barra-corpo" style="width:{min(abs(direcao), 100)}%; background:{cor_direcao};"></div>
            </div>
            
            <div class="label-bio">Pressão (Rejeição/Pavio)</div>
            <div class="barra-fundo">
                <div class="barra-pavio" style="width:{min(pressao, 100)}%;"></div>
            </div>
        </div>
    """

    if dados['tipo']:
        cor_alerta = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
        html_painel += f"""
        <div style="border-top: 1px solid #30363d; margin-top:15px; padding-top:15px;">
            <b style="color:{cor_alerta}; font-size:1.2rem;">{dados['tipo']} DETECTADA</b><br>
            <code style="color:#58a6ff;">ZONA: {dados['z_inf']:.5f} — {dados['z_sup']:.5f}</code>
            <div style="display:grid; grid-template-columns: 1fr 1fr; margin-top:10px;">
                <div><small style="color:#3fb950;">ALVOS (TP)</small><br><b>{dados['tp'][0]:.5f}</b></div>
                <div><small style="color:#f85149;">RISCO (SL)</small><br><b>{dados['sl'][0]:.5f}</b></div>
            </div>
        </div>
        """
    else:
        html_painel += '<div style="text-align:center; color:#30363d; font-size:0.75rem; margin-top:15px;">VARREDURA ATIVA...</div>'
    
    html_painel += "</div>"
    
    # O comando abaixo é o que desenha as barras na tela corretamente
    st.markdown(html_painel, unsafe_allow_html=True)
