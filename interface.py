import streamlit as st

def aplicar_estilo_v15():
    st.markdown("""
        <style>
        .stApp { background-color: #05070a; color: #ffffff; }
        .bloco-card { background: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
        .barra-fundo { background: #161b22; height: 10px; border-radius: 5px; margin-bottom: 10px; overflow: hidden; }
        .barra-preenchimento { height: 100%; transition: 0.5s; }
        .texto-mini { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

def desenhar_radar(titulo, dados):
    score = dados['score']
    direcao = dados['direcao']
    pressao = dados['pressao']
    
    cor_corpo = "#3fb950" if direcao > 0 else "#f85149"
    largura_corpo = min(abs(direcao), 100)
    
    with st.container():
        # Usamos st.write com componentes HTML injetados via Markdown para evitar erro de texto
        st.markdown(f"""
        <div class="bloco-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1rem; font-weight:bold;">{titulo}</span>
                <span style="color:#58a6ff; font-size:0.8rem;">PRONTIDÃO: {score:.1f}%</span>
            </div>
            
            <div style="margin-top:10px;">
                <div class="texto-mini">Direção (Corpo do Candle)</div>
                <div class="barra-fundo">
                    <div class="barra-preenchimento" style="width:{largura_corpo}%; background:{cor_corpo};"></div>
                </div>
                
                <div class="texto-mini">Pressão (Pavio/Rejeição)</div>
                <div class="barra-fundo">
                    <div class="barra-preenchimento" style="width:{pressao}%; background:#f1e05a;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if dados['tipo']:
            cor_alerta = "#3fb950" if dados['tipo'] == "COMPRA" else "#f85149"
            st.markdown(f"""
                <div style="border-top:1px solid #30363d; padding-top:10px;">
                    <b style="color:{cor_alerta}; font-size:1.1rem;">{dados['tipo']} ATIVA</b><br>
                    <code style="color:#58a6ff; font-size:0.8rem;">ZONA: {dados['z_inf']:.5f} — {dados['z_sup']:.5f}</code>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;">
                        <div><span class="texto-mini" style="color:#3fb950;">LUCRO (TP)</span><br><b>{dados['tp'][0]:.5f}</b><br><b>{dados['tp'][1]:.5f}</b></div>
                        <div><span class="texto-mini" style="color:#f85149;">RISCO (SL)</span><br><b>{dados['sl'][0]:.5f}</b><br><b>{dados['sl'][1]:.5f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:10px; font-size:0.7rem; color:#444;'>VARREDURA INSTITUCIONAL ATIVA...</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
