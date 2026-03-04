import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Coleta otimizada: 1 mês de dados 15m para cálculo de volatilidade
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        offset = 0.0030 # Sincronia MT5 (-30 Pips)
        df = data[['Open', 'High', 'Low', 'Close']].copy() - offset
        df.columns = ['open', 'high', 'low', 'close']
        
        # Cálculo de Pips Diário com extração escalar pura (evita FutureWarning)
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_atual = float(df['close'].iloc[-1])
        p_ontem_series = dados_diarios['Close'].iloc[-2]
        p_ontem = float(np.reshape(p_ontem_series.values, -1)[0]) - offset
        
        pips_diff = (p_atual - p_ontem) * 10000
        return df, pips_diff
    except Exception:
        return pd.DataFrame(), 0.0

def detectar_tendencia_macro(df):
    try:
        # Regressão Linear para identificar o viés institucional (Bull/Bear)
        y = df['close'].tail(80).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        slope = float(model.coef_[0][0])
        if slope > 0.000006: return "ALTA (BULLISH)"
        if slope < -0.000006: return "BAIXA (BEARISH)"
        return "LATERAL"
    except: return "INDEFINIDA"

def motor_auraxis_v15(df, modo):
    # Musculatura de Janelas: Curta, Média e Longa
    janelas = {"SCALPER": 24, "DAY": 60, "SWING": 120}
    p = janelas.get(modo, 60)
    window = df.tail(p + 5).copy()
    
    # Cálculo de Z-Score (Mede a distorção do preço em relação à média)
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    
    # ATR para definição de alvos institucionais
    atr = float((window['high'] - window['low']).mean())
    p_atual = float(window['close'].iloc[-1])
    
    # Zonas de Liquidez e Exaustão
    res = {
        "tipo": None, "score": min((abs(z_atual) / 2.5) * 100, 100.0),
        "z": z_atual, "p_atual": p_atual, "atr": atr,
        "z_sup": p_atual + (atr * 2.0), "z_inf": p_atual - (atr * 2.0)
    }

    # Lógica de Reversão de Média: Entra na exaustão, sai no alvo oposto
    if abs(z_atual) > 2.1:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"], res["sl"] = res["z_sup"], res["z_inf"] - (atr * 0.5)
        else:
            res["tp1"], res["sl"] = res["z_inf"], res["z_sup"] + (atr * 0.5)
            
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
