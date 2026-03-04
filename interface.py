import streamlit as st

def exibir_radar_auraxis(titulo, dados):
    # Cores baseadas na direção (Verde para alta, Vermelho para baixa)
    cor_direcao = "#3fb950" if dados['direcao'] > 0 else "#f85149"
    
    # Criando a estrutura visual
    html = f"""
    <div style="background:#0d1117; border:1px solid #30363d; padding:15px; border-radius:10px; margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between;">
            <b style="color:white;">{titulo}</b>
            <span style="color:#58a6ff;">PRONTIDÃO: {dados['score']:.1f}%</span>
        </div>
        <div style="margin-top:10px;">
            <div style="font-size:0.7rem; color:#8b949e;">DIREÇÃO (CORPO DO CANDLE)</div>
            <div style="background:#161b22; height:8px; border-radius:4px;">
                <div style="width:{abs(dados['direcao'])}%; background:{cor_direcao}; height:100%;"></div>
            </div>
            <div style="font-size:0.7rem; color:#8b949e; margin-top:5px;">PRESSÃO (REJEIÇÃO/PAVIO)</div>
            <div style="background:#161b22; height:8px; border-radius:4px;">
                <div style="width:{dados['pressao']}%; background:#f1e05a; height:100%;"></div>
            </div>
        </div>
    </div>
    """
    # O SEGREDO ESTÁ AQUI: unsafe_allow_html=True desenha as barras na tela
    st.markdown(html, unsafe_allow_html=True)
