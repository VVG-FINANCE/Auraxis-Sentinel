import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Puxa dados para análise de desvio padrão
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        preco_atual = float(data['Close'].iloc[-1])
        # Variação diária em PIPS
        p_ontem = float(yf.download(ticker, period="2d", interval="1d", progress=False)['Close'].iloc[-2])
        pips_hoje = (preco_atual - p_ontem) * 10000
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, float(pips_hoje)
    except:
        return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    # Janelas de amostragem institucional
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 180}
    p = janelas[modo]
    window = df.tail(p).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # --- BIOMETRIA (Corpo vs Pavio) ---
    ab, mx, mn, fe = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo = fe - ab
    faixa = (mx - mn) + 1e-9
    
    direcao_v = (corpo / faixa) * 100
    pressao_v = ((mx - max(ab, fe)) + (min(ab, fe) - mn)) / faixa * 100

    # --- MUSCULATURA ESTATÍSTICA (Z-Score) ---
    precos = window['close'].values.reshape(-1, 1)
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(precos)
    z_atual = z_scores[-1][0]
    
    # Prontidão de 0 a 100%
    prontidao = min(abs(z_atual) / 2.0, 1.0) * 100
    atr = (window['high'] - window['low']).mean()

    res = {
        "tipo": None, "score": prontidao, "direcao": direcao_v, 
        "pressao": pressao_v, "z_inf": p_atual - (atr * 0.3), "z_sup": p_atual + (atr * 0.3)
    }

    # Gatilho de Operação
    if abs(z_atual) > 1.6 and (abs(corpo)/faixa) > 0.3:
        res["tipo"] = "COMPRA" if z_atual > 0 else "VENDA"
        m = 1 if res["tipo"] == "COMPRA" else -1
        mult = {"SCALPER": 1.4, "DAY": 2.7, "SWING": 4.5, "POSITION": 7.0}[modo]
        
        res.update({
            "tp": [p_atual + (atr * mult * m), p_atual + (atr * mult * 1.5 * m)],
            "sl": [p_atual - (atr * mult * 0.8 * m), p_atual - (atr * mult * 1.2 * m)]
        })
    return res
