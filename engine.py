import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Baixa dados 15m e 1d de uma só vez para evitar Rate Limit
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        offset = 0.0030
        df = data[['Open', 'High', 'Low', 'Close']].copy() - offset
        df.columns = ['open', 'high', 'low', 'close']
        
        # Correção do FutureWarning: iloc[0] explícito
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_atual = float(df['close'].iloc[-1])
        # Pegando o valor escalar corretamente para evitar o erro do log
        p_ontem = float(dados_diarios['Close'].iloc[-2]) - offset
        pips_diff = (p_atual - p_ontem) * 10000
        
        return df, pips_diff
    except Exception as e:
        print(f"Erro na coleta: {e}")
        return pd.DataFrame(), 0.0

def detectar_tendencia_macro(df_15m):
    """Usa o DF já baixado para não fazer nova requisição"""
    try:
        y = df_15m['close'].tail(100).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        inc = model.coef_[0][0]
        if inc > 0.000005: return "ALTA (BULLISH)"
        if inc < -0.000005: return "BAIXA (BEARISH)"
        return "LATERAL"
    except: return "INDEFINIDA"

def motor_auraxis_v15(df, modo):
    # Janelas estratégicas mantidas e protegidas
    janelas = {"SCALPER": 20, "DAY": 50, "SWING": 100}
    p = janelas.get(modo, 50)
    window = df.tail(p + 5).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # Cálculo de Z-Score e ATR (Musculatura Intacta)
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    atr = (window['high'] - window['low']).mean()
    
    # Zonas de Liquidez
    z_sup = p_atual + (atr * 1.6)
    z_inf = p_atual - (atr * 1.6)
    
    score = min((abs(z_atual) / 2.2) * 100, 100.0)
    
    res = {
        "tipo": None, "score": score, "z": z_atual, 
        "p_atual": p_atual, "z_sup": z_sup, "z_inf": z_inf, "atr": atr
    }

    # Estratégia de Reversão em Zonas Extremas
    if abs(z_atual) > 1.8:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"] = z_sup
            res["sl"] = z_inf - (atr * 0.8)
        else:
            res["tp1"] = z_inf
            res["sl"] = z_sup + (atr * 0.8)
            
    return res
