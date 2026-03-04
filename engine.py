import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

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
        
        # AJUSTE MT5: -30 Pips
        def ajustar_preco(val):
            v = float(val.iloc[0]) if hasattr(val, "__len__") else float(val)
            return v - 0.0030

        p_atual = ajustar_preco(data['Close'].iloc[-1])
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_ontem = ajustar_preco(dados_diarios['Close'].iloc[-2])
        pips_diff = (p_atual - p_ontem) * 10000
        
        df = data[['Open', 'High', 'Low', 'Close']].copy() - 0.0030
        df.columns = ['open', 'high', 'low', 'close']
        return df, pips_diff
    except: return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 150}
    p = janelas.get(modo, 35)
    window = df.tail(p + 3).copy()
    p_atual = float(window['close'].iloc[-1])
    
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    atr = (window['high'] - window['low']).mean()
    
    fvg = (window['low'].iloc[-1] > window['high'].iloc[-3]) or (window['high'].iloc[-1] < window['low'].iloc[-3])

    zona_sup = p_atual + (atr * 1.5)
    zona_inf = p_atual - (atr * 1.5)
    
    score = min((abs(z_atual) / 2.0) * 100, 100.0)
    if fvg: score = min(score + 15, 100.0)

    res = {"tipo": None, "score": score, "z": z_atual, "fvg": fvg, "p_atual": p_atual, "z_sup": zona_sup, "z_inf": zona_inf}

    if abs(z_atual) > 1.5:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"], res["sl"] = res["z_sup"], res["z_inf"] - (atr * 0.5)
        else:
            res["tp1"], res["sl"] = res["z_inf"], res["z_sup"] + (atr * 0.5)
    return res

def verificar_desfecho(preco_atual, trade_aberto):
    if trade_aberto['tipo'] == "COMPRA":
        if preco_atual >= trade_aberto['tp1']: return "WIN"
        if preco_atual <= trade_aberto['sl']: return "LOSS"
    else:
        if preco_atual <= trade_aberto['tp1']: return "WIN"
        if preco_atual >= trade_aberto['sl']: return "LOSS"
    return None
