import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from datetime import datetime

# CONFIGURAÇÃO DA SUA API
API_KEY = "SUA_CHAVE_AQUI" 

def detectar_tendencia_macro(ticker="EURUSD=X"):
    try:
        data = yf.download(ticker, period="5d", interval="60m", progress=False)
        if data.empty: return "NEUTRA", 0.0
        y = data['Close'].tail(50).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        inclinacao = model.coef_[0][0]
        if inclinacao > 0.00001: return "ALTA (BULLISH)", inclinacao
        elif inclinacao < -0.00001: return "BAIXA (BEARISH)", inclinacao
        else: return "LATERAL (RANGE)", inclinacao
    except: return "INDEFINIDA", 0.0

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        # Extração segura para evitar FutureWarning
        ultimo_val = data['Close'].iloc[-1]
        p_atual = float(ultimo_val.iloc[0]) if hasattr(ultimo_val, "__len__") else float(ultimo_val)
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_ontem = float(dados_diarios['Close'].iloc[-2])
        pips_diff = (p_atual - p_ontem) * 10000
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, pips_diff
    except: return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 150}
    p = janelas.get(modo, 35)
    window = df.tail(p + 3).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # Biometria
    ab, mx, mn, fe = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo, faixa = (fe - ab), ((mx - mn) + 1e-9)
    direcao_bio = (corpo / faixa) * 100
    pressao_rejeicao = (((mx - max(ab, fe)) + (min(ab, fe) - mn)) / faixa) * 100

    # Z-Score
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    
    # Fair Value Gap (FVG)
    fvg_confirmado = (window['low'].iloc[-1] > window['high'].iloc[-3]) or (window['high'].iloc[-1] < window['low'].iloc[-3])

    # Score e Probabilidade
    score_base = min(abs(z_atual) / 2.0, 1.0) * 100
    if fvg_confirmado: score_base += 15 
    
    atr = (window['high'] - window['low']).mean()
    res = {"tipo": None, "score": min(score_base, 100.0), "direcao": direcao_bio, "pressao": pressao_rejeicao, "fvg": fvg_confirmado, "z": z_atual}

    if abs(z_atual) > 1.6 and fvg_confirmado:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        mult = {"SCALPER": 1.5, "DAY": 2.5, "SWING": 4.0, "POSITION": 6.0}[modo]
        direcao_m = 1 if res["tipo"] == "COMPRA" else -1
        res.update({"tp": p_atual + (atr * mult * direcao_m), "sl": p_atual - (atr * mult * 0.7 * direcao_m)})
    return res
