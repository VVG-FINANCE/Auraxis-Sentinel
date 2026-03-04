import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Puxa dados de 15m para cálculos e 1d para variação diária
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        # Ajuste MT5: -30 Pips (0.0030)
        offset = 0.0030
        df = data[['Open', 'High', 'Low', 'Close']].copy() - offset
        df.columns = ['open', 'high', 'low', 'close']
        
        # Cálculo de Pips Hoje
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_atual = float(df['close'].iloc[-1])
        p_ontem = float(dados_diarios['Close'].iloc[-2]) - offset
        pips_diff = (p_atual - p_ontem) * 10000
        
        return df, pips_diff
    except: return pd.DataFrame(), 0.0

def detectar_tendencia_macro(ticker="EURUSD=X"):
    try:
        data = yf.download(ticker, period="5d", interval="60m", progress=False)
        y = data['Close'].tail(50).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        inc = model.coef_[0][0]
        if inc > 0.00001: return "ALTA (BULLISH)"
        if inc < -0.00001: return "BAIXA (BEARISH)"
        return "LATERAL"
    except: return "INDEFINIDA"

def motor_auraxis_v15(df, modo):
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75}
    p = janelas.get(modo, 35)
    window = df.tail(p + 3).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # Cálculos de Volatilidade e Z-Score
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    atr = (window['high'] - window['low']).mean()
    
    # Definição de Zonas (Superior e Inferior)
    z_sup = p_atual + (atr * 1.5)
    z_inf = p_atual - (atr * 1.5)
    
    # Score de Prontidão
    score = min((abs(z_atual) / 2.0) * 100, 100.0)
    
    res = {
        "tipo": None, "score": score, "z": z_atual, 
        "p_atual": p_atual, "z_sup": z_sup, "z_inf": z_inf, "atr": atr
    }

    # Estratégia das Zonas: Entradas e Alvos nos limites
    if abs(z_atual) > 1.5:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"] = z_sup
            res["sl"] = z_inf - (atr * 0.5)
        else:
            res["tp1"] = z_inf
            res["sl"] = z_sup + (atr * 0.5)
            
    return res

def verificar_desfecho(p_atual, t):
    if t['tipo'] == "COMPRA":
        if p_atual >= t['tp1']: return "WIN"
        if p_atual <= t['sl']: return "LOSS"
    else:
        if p_atual <= t['tp1']: return "WIN"
        if p_atual >= t['sl']: return "LOSS"
    return None
