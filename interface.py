import streamlit as st

def configurar_layout():
    """
    Injeta o CSS para criar o visual escuro (Dark Mode) e 
    estilizar os cards e barras de biometria.
    """
    st.markdown("""
        <style>
        /* Fundo do App */
        .stApp { background-color: #05070a; color: #ffffff; }
        
        /* Estilo do Card Auraxis */
        .card-auraxis { 
            background: #0d1117; 
            border: 1px solid #30363d; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 15px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        /* Barras de Biometria */
        .barra-fundo { 
            background: #161b22; 
            height: 10px; 
            border-radius: 5px; 
            margin: 8px 0; 
            overflow: hidden; 
        }
        .barra-preenchimento { 
            height: 100%; 
            transition: width 0.8s ease-in-out; 
        }
        
        /* Rótulos e Textos */
        .texto-id { 
            font-size: 0.65rem; 
            color: #8b949e; 
            font-weight: bold; 
            text-transform: uppercase; 
            letter-spacing: 1px;
        }
        
        /* Animação para Sinal Ativo */
        @keyframes pulsar {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }
        .sinal-ativo { animation: pulsar 2s infinite; }
        </style>
    """, unsafe_allow_html=True)

def exibir_modulo(titulo, dados):
    """
    Renderiza o card visual. Se houver sinal ativo, 
    mostra os dados de Entrada (Zona), TP e SL.
    """
    score = dados.get('score', 0)
    direcao = dados.get('direcao', 0)
    pressao = dados.get('pressao', 0)
    tipo_sinal = dados.get('tipo') # COMPRA, VENDA ou None
    
    # Define a cor da barra de direção
    cor_direcao = "#3fb950" if direcao > 0 else "#f85149"
    
    # Início da construção do HTML
    conteudo_html = f"""
    <div class="card-auraxis">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <b style="font-size:1.1rem; color:#f0f6fc;">{titulo}</b>
            <span style="color:#58a6ff; font-family:monospace; font-weight:bold;">PRONTIDÃO: {score:.1f}%</span>
        </div>
        
        <div style="margin-top:15px;">
            <div class="texto-id">Direção (Fluxo Institucional)</div>
            <div class="barra-fundo">
                <div class="barra-preenchimento" style="width:{min(abs(direcao), 100)}%; background:{cor_direcao};"></div>
            </div>
            
            <div class="texto-id">Pressão (Rejeição de Preço)</div>
            <div class="barra-fundo">
                <div class="barra-preenchimento" style="width:{min(pressao, 100)}%; background:#f1e05a;"></div>
            </div>
        </div>
    """

    # Lógica para mostrar DADOS DE ENTRADA quando o sinal estiver ATIVO
    if tipo_sinal:
        cor_sinal = "#3fb950" if tipo_sinal == "COMPRA" else "#f85149"
        conteudo_html += f"""
        <div class="sinal-ativo" style="border-top: 1px solid #30363d; margin-top:15px; padding-top:15px;">
            <b style="color:{cor_sinal}; font-size:1.2rem;">{tipo_sinal} IDENTIFICADA</b><br>
            
            <div style="background:#161b22; padding:10px; border-radius:6px; margin-top:10px; border-left:4px solid {cor_sinal};">
                <small style="color:#8b949e;">ZONA DE ATUAÇÃO</small><br>
                <code style="color:#f0f6fc; font-size:1rem;">{dados['z_inf']:.5f} — {dados['z_sup']:.5f}</code>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:10px;">
                <div style="background:#1c2128; padding:8px; border-radius:6px;">
                    <small style="color:#3fb950; font-weight:bold;">ALVO (TP)</small><br>
                    <b style="font-size:0.9rem;">{dados['tp'][0]:.5f}</b>
                </div>
                <div style="background:#1c2128; padding:8px; border-radius:6px;">
                    <small style="color:#f85149; font-weight:bold;">RISCO (SL)</small><br>
                    <b style="font-size:0.9rem;">{dados['sl'][0]:.5f}</b>
                </div>
            </div>
        </div>
        """
    else:
        # Estado de espera (O que aparece na imagem que você enviou, mas agora formatado)
        conteudo_html += """
        <div style="text-align:center; color:#30363d; font-size:0.75rem; margin-top:20px; letter-spacing:2px; font-weight:bold;">
            VARREDURA DE LIQUIDEZ...
        </div>
        """
    
    conteudo_html += "</div>"
    
    # A LINHA QUE RESOLVE SEU PROBLEMA:
    st.markdown(conteudo_html, unsafe_allow_html=True)
