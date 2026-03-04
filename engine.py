import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler

def obter_dados_institucionais(ticker="EURUSD=X"):
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

def motor_auraxis_v15(df, modo="DAY"):
    p_atual = float(df['close'].iloc[-1])
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 180}
    p = janelas[modo]
    window = df.tail(p).copy()
    
    # --- Anatomia do Candle (Biometria) ---
    c_open, c_high, c_low, c_close = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo_real = c_close - c_open
    faixa_total = (c_high - c_low) + 1e-9
    
    direcao_bio = (corpo_real / faixa_total) * 100
    pavio_rejeicao = ((c_high - max(c_open, c_close)) + (min(c_open, c_close) - c_low)) / faixa_total * 100

    # --- Musculatura Estratégica (Z-Score) ---
    precos = window['close'].values.reshape(-1, 1)
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(precos)
    z_atual = z_scores[-1][0]
    
    score_prontidao = min(abs(z_atual) / 2.0, 1.0) * 100
    atr = (window['high'] - window['low']).mean()

    res = {
        "tipo": None, "score": score_prontidao, "direcao": direcao_bio, 
        "pressao": pavio_rejeicao, "z_inf": p_atual - (atr * 0.3), "z_sup": p_atual + (atr * 0.3)
    }

    # Gatilho Institucional
    if abs(z_atual) > 1.5 and (abs(corpo_real)/faixa_total) > 0.3:
        tipo = "COMPRA" if z_atual > 0 else "VENDA"
        m_alvo = {"SCALPER": 1.3, "DAY": 2.5, "SWING": 4.0, "POSITION": 6.0}[modo]
        direcao_m = 1 if tipo == "COMPRA" else -1
        
        res.update({
            "tipo": tipo,
            "tp": [p_atual + (atr * m_alvo * direcao_m), p_atual + (atr * m_alvo * 1.6 * direcao_m)],
            "sl": [p_atual - (atr * m_alvo * 0.7 * direcao_m), p_atual - (atr * m_alvo * 1.2 * direcao_m)]
        })
    return res
