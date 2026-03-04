import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        offset = 0.0030 # Ajuste MT5
        df = data[['Open', 'High', 'Low', 'Close']].copy() - offset
        df.columns = ['open', 'high', 'low', 'close']
        
        # --- CORREÇÃO DEFINITIVA DO FUTUREWARNING ---
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_atual = float(df['close'].iloc[-1])
        
        # Usamos .item() ou iloc[0] após converter para valores puros para garantir que seja um float escalar
        p_ontem_raw = dados_diarios['Close'].iloc[-2]
        p_ontem = float(np.array(p_ontem_raw).flatten()[0]) - offset
        
        pips_diff = (p_atual - p_ontem) * 10000
        return df, pips_diff
    except Exception as e:
        print(f"Erro YFinance: {e}")
        return pd.DataFrame(), 0.0

def detectar_tendencia_macro(df):
    try:
        y = df['close'].tail(100).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        coef = float(model.coef_[0][0])
        if coef > 0.000005: return "ALTA (BULLISH)"
        if coef < -0.000005: return "BAIXA (BEARISH)"
        return "LATERAL"
    except: return "INDEFINIDA"

def motor_auraxis_v15(df, modo):
    janelas = {"SCALPER": 20, "DAY": 55, "SWING": 110}
    p = janelas.get(modo, 55)
    window = df.tail(p + 5).copy()
    p_atual = float(window['close'].iloc[-1])
    
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    atr = float((window['high'] - window['low']).mean())
    
    z_sup = p_atual + (atr * 1.8)
    z_inf = p_atual - (atr * 1.8)
    score = min((abs(z_atual) / 2.5) * 100, 100.0)
    
    res = {"tipo": None, "score": score, "z": z_atual, "p_atual": p_atual, "z_sup": z_sup, "z_inf": z_inf, "atr": atr}

    if abs(z_atual) > 1.9:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"], res["sl"] = z_sup, z_inf - (atr * 0.7)
        else:
            res["tp1"], res["sl"] = z_inf, z_sup + (atr * 0.7)
    return res

def verificar_desfecho(p_atual, t):
    p = float(p_atual)
    if t['tipo'] == "COMPRA":
        if p >= float(t['tp1']): return "WIN"
        if p <= float(t['sl']): return "LOSS"
    elif t['tipo'] == "VENDA":
        if p <= float(t['tp1']): return "WIN"
        if p >= float(t['sl']): return "LOSS"
    return None
