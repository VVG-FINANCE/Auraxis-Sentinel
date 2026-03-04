import pandas as pd
import numpy as np
import yfinance as yf

def obter_dados_hifi(ticker="EURUSD=X"):
    try:
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        p_atual = float(data['Close'].iloc[-1])
        p_ontem = float(yf.download(ticker, period="2d", interval="1d", progress=False)['Close'].iloc[-2])
        pips_diff = (p_atual - p_ontem) * 10000
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, float(pips_diff)
    except:
        return pd.DataFrame(), 0.0

def motor_neural_v15(df, modo="DAY"):
    p_atual = float(df['close'].iloc[-1])
    # Configuração de períodos por perfil
    config = {"SCALPER": 12, "DAY": 26, "SWING": 60, "POSITION": 150}
    p = config[modo]
    window = df.tail(p)
    
    # --- Anatomia do Candle (Corpo vs Pavio) ---
    c_open, c_high, c_low, c_close = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo = c_close - c_open
    total_range = (c_high - c_low) + 1e-9
    
    # Indicadores Visuais (0 a 100)
    direcao_val = (corpo / total_range) * 100 # Positivo (Alta), Negativo (Baixa)
    pavio_sup = c_high - max(c_open, c_close)
    pavio_inf = min(c_open, c_close) - c_low
    pressao_val = ((pavio_sup + pavio_inf) / total_range) * 100

    # --- Score Institucional ---
    ma = window['close'].mean()
    std = window['close'].std() + 1e-9
    z_score = (p_atual - ma) / std
    score_pronto = min(abs(z_score) / 1.4, 1.0) * 100
    
    atr = (window['high'] - window['low']).mean()
    z_inf, z_sup = p_atual - (atr * 0.25), p_atual + (atr * 0.25)

    res = {
        "tipo": None, "score": score_pronto, "direcao": direcao_val, 
        "pressao": pressao_val, "z_inf": z_inf, "z_sup": z_sup
    }

    # Gatilho de Entrada (Z-Score > 1.4 e corpo mínimo de 30%)
    if abs(z_score) > 1.4 and (abs(corpo)/total_range) > 0.3:
        tipo = "COMPRA" if z_score > 0 else "VENDA"
        m = 1 if tipo == "COMPRA" else -1
        # Multiplicadores de Alvo
        mult = {"SCALPER": 1.2, "DAY": 2.4, "SWING": 3.8, "POSITION": 5.5}[modo]
        
        res.update({
            "tipo": tipo,
            "tp": [p_atual + (atr * mult * m), p_atual + (atr * mult * 1.5 * m)],
            "sl": [p_atual - (atr * mult * 0.8 * m), p_atual - (atr * mult * 1.1 * m)]
        })
    
    return res
