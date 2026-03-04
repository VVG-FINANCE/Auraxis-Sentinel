import streamlit as st

def configurar_layout_soberano():
    """Configura o visual escuro e as barras dinâmicas."""
    st.markdown("""
        <style>
        .stApp { background-color: #05070a; color: #ffffff; }
        .card-auraxis { 
            background: #0d1117; border: 1px solid #30363d; border-radius: 12px; 
            padding: 20px; margin-bottom: 15px; 
        }
        .barra-fundo { background: #161b22; height: 12px; border-radius: 6px; margin: 10px 0; overflow: hidden; }
        .barra-preenchimento { height: 100%; transition: width 0.8s ease-in-out; }
        .label-institucional { font-size: 0.7rem; color: #8b949e; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)

def exibir_modulo_auraxis(titulo, dados):
    """Desenha os indicadores de Direção e Pressão com musculatura visual."""
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    cor_direcao = "#3fb950" if direcao > 0 else "#f85149"
    
    html = f"""
    <div class="card-auraxis">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <b style="font-size:1.1rem; color:#f0f6fc;">{titulo}</b>
            <span style="color:#58a6ff; font-family: 'Roboto Mono', monospace;">CONFIANÇA: {score:.1f}%</span>
        </div>
        
        <div class="label-institucional">Direção do Fluxo (Corpo)</div>
        <div class="barra-fundo">
            <div class="barra-preenchimento" style="width:{min(abs(direcao), 100)}%; background:{cor_direcao};"></div>
        </div>
        
        <div class="label-institucional">Pressão de Rejeição (Pavio)</div>
        <div class="barra-fundo">
            <div class="barra-preenchimento" style="width:{min(pressao, 100)}%; background:#f1e05a;"></div>
        </div>
    """

    if dados['tipo']:
        cor_sinal = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
        html += f"""
        <div style="border-top: 1px solid #30363d; margin-top:15px; padding-top:15px; animation: pulse 2s infinite;">
            <b style="color:{cor_sinal}; font-size:1.2rem;">{dados['tipo']} IDENTIFICADA</b><br>
            <div style="display:grid; grid-template-columns: 1fr 1fr; margin-top:10px; gap: 10px;">
                <div style="background:#1c2128; padding:8px; border-radius:6px; border-left:3px solid #3fb950;">
                    <small style="color:#8b949e;">ALVO (TP)</small><br><b style="color:#3fb950;">{dados['tp'][0]:.5f}</b>
                </div>
                <div style="background:#1c2128; padding:8px; border-radius:6px; border-left:3px solid #f85149;">
                    <small style="color:#8b949e;">RISCO (SL)</small><br><b style="color:#f85149;">{dados['sl'][0]:.5f}</b>
                </div>
            </div>
        </div>
        """
    else:
        html += '<div style="text-align:center; color:#30363d; font-size:0.7rem; margin-top:15px; letter-spacing:2px;">MONITORANDO LIQUIDEZ...</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
