import streamlit as st

def exibir_radar_institucional(titulo, dados):
    # Tradução e Musculatura Visual
    score = dados['score']
    direcao = dados['direcao']
    cor_barra = "#3fb950" if direcao > 0 else "#f85149"
    
    # O SEGREDO: Usar st.markdown com unsafe_allow_html=True
    st.markdown(f"""
    <div style="background:#0d1117; border:1px solid #30363d; padding:15px; border-radius:10px;">
        <div style="display:flex; justify-content:space-between;">
            <b style="color:white;">{titulo}</b>
            <span style="color:#58a6ff;">SCORE: {score:.1f}%</span>
        </div>
        <div style="margin-top:10px;">
            <div style="font-size:0.7rem; color:#8b949e;">DIREÇÃO (FORÇA REAL)</div>
            <div style="background:#161b22; height:8px; border-radius:4px;">
                <div style="width:{abs(direcao)}%; background:{cor_barra}; height:100%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True) # <-- ISSO CORRIGE O PRINT 1819
