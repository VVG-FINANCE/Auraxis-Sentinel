import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Puxa dados com folga para cálculo estatístico
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        preco_atual = float(data['Close'].iloc[-1])
        # Cálculo de Pips diários
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        preco_ontem = float(dados_diarios['Close'].iloc[-2])
        pips_hoje = (preco_atual - preco_ontem) * 10000
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, float(pips_hoje)
    except Exception as e:
        return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    # Parâmetros de Musculatura por Perfil
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 180}
    p = janelas[modo]
    window = df.tail(p).copy()
    preco_atual = float(window['close'].iloc[-1])
    
    # --- BIOMETRIA DO CANDLE (Leitura Visual de Direção e Força) ---
    abertura, maxima, minima, fechamento = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo = fechamento - abertura
    faixa_total = (maxima - minima) + 1e-9
    
    # Indicador de Direção (Corpo) e Pressão (Pavio/Rejeição)
    direcao_v = (corpo / faixa_total) * 100
    pavio_superior = maxima - max(abertura, fechamento)
    pavio_inferior = min(abertura, fechamento) - minima
    pressao_v = ((pavio_superior + pavio_inferior) / faixa_total) * 100

    # --- ENGENHARIA ESTATÍSTICA (Scikit-Learn) ---
    precos = window['close'].values.reshape(-1, 1)
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(precos)
    z_atual = z_scores[-1][0]
    
    # Score de Prontidão Institucional (0 a 100%)
    score_prontidao = min(abs(z_atual) / 2.0, 1.0) * 100
    
    # Cálculo de Alvos e Riscos via ATR
    atr = (window['high'] - window['low']).mean()
    zona_inf, zona_sup = preco_atual - (atr * 0.25), preco_atual + (atr * 0.25)

    res = {
        "tipo": None, "score": score_prontidao, "direcao": direcao_v, 
        "pressao": pressao_v, "z_inf": zona_inf, "z_sup": zona_sup
    }

    # Lógica de Gatilho (Confiança Neural > 1.5 desvios)
    if abs(z_atual) > 1.5 and (abs(corpo)/faixa_total) > 0.3:
        tipo = "COMPRA" if z_atual > 0 else "VENDA"
        direcao_m = 1 if tipo == "COMPRA" else -1
        multiplicador = {"SCALPER": 1.3, "DAY": 2.6, "SWING": 4.2, "POSITION": 6.5}[modo]
        
        res.update({
            "tipo": tipo,
            "tp": [preco_atual + (atr * multiplicador * direcao_m), preco_atual + (atr * multiplicador * 1.5 * direcao_m)],
            "sl": [preco_atual - (atr * multiplicador * 0.8 * direcao_m), preco_atual - (atr * multiplicador * 1.2 * direcao_m)]
        })
    
    return res
