import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Coleta de dados com tratamento de erro
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        offset = 0.0030 # Ajuste de -30 pips para MT5
        
        # Criando o DF ajustado
        df = data[['Open', 'High', 'Low', 'Close']].copy() - offset
        df.columns = ['open', 'high', 'low', 'close']
        
        # Cálculo de Pips Hoje (Corrigindo o FutureWarning dos logs)
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_atual = float(df['close'].iloc[-1])
        # A correção abaixo remove o erro "Calling float on a single element Series"
        p_ontem = float(dados_diarios['Close'].iloc[-2]) - offset
        pips_diff = (p_atual - p_ontem) * 10000
        
        return df, pips_diff
    except Exception as e:
        print(f"Erro YFinance: {e}")
        return pd.DataFrame(), 0.0

def detectar_tendencia_macro(df):
    try:
        # Regressão linear nos últimos 100 candles de 15m
        y = df['close'].tail(100).values.reshape(-1, 1)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        if model.coef_[0][0] > 0.000005: return "ALTA (BULLISH)"
        if model.coef_[0][0] < -0.000005: return "BAIXA (BEARISH)"
        return "LATERAL"
    except: return "INDEFINIDA"

def motor_auraxis_v15(df, modo):
    # Musculatura de Janelas Temporais
    janelas = {"SCALPER": 20, "DAY": 55, "SWING": 110}
    p = janelas.get(modo, 55)
    
    window = df.tail(p + 5).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # Z-Score (Exaustão de Preço)
    precos = window['close'].values.reshape(-1, 1)
    z_atual = float(StandardScaler().fit_transform(precos)[-1][0])
    
    # ATR para Zonas Dinâmicas
    atr = (window['high'] - window['low']).mean()
    
    # Limites da Estratégia de Zonas
    z_sup = p_atual + (atr * 1.8)
    z_inf = p_atual - (atr * 1.8)
    
    # Cálculo de Prontidão (Score)
    score = min((abs(z_atual) / 2.5) * 100, 100.0)
    
    res = {
        "tipo": None, "score": score, "z": z_atual, 
        "p_atual": p_atual, "z_sup": z_sup, "z_inf": z_inf, "atr": atr
    }

    # Lógica de Entrada em Zonas de Exaustão
    if abs(z_atual) > 1.9:
        res["tipo"] = "COMPRA" if z_atual < 0 else "VENDA"
        if res["tipo"] == "COMPRA":
            res["tp1"] = z_sup  # Alvo na zona superior
            res["sl"] = z_inf - (atr * 0.7) # Stop abaixo da zona inferior
        else:
            res["tp1"] = z_inf  # Alvo na zona inferior
            res["sl"] = z_sup + (atr * 0.7) # Stop acima da zona superior
            
    return res

def verificar_desfecho(p_atual, t):
    if t['tipo'] == "COMPRA":
        if p_atual >= t['tp1']: return "WIN"
        if p_atual <= t['sl']: return "LOSS"
    elif t['tipo'] == "VENDA":
        if p_atual <= t['tp1']: return "WIN"
        if p_atual >= t['sl']: return "LOSS"
    return None
