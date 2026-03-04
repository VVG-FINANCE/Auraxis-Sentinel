import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Puxa 1 mês de dados em intervalos de 15min
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        # Preço atual e cálculo de Pips do dia
        p_atual = float(data['Close'].iloc[-1])
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_ontem = float(dados_diarios['Close'].iloc[-2])
        pips_diff = (p_atual - p_ontem) * 10000
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, float(pips_diff)
    except:
        return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    # Janelas de análise institucional
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 150}
    p = janelas.get(modo, 35)
    window = df.tail(p).copy()
    p_atual = float(window['close'].iloc[-1])
    
    # --- BIOMETRIA DO CANDLE (Direção e Pressão) ---
    ab, mx, mn, fe = window['open'].iloc[-1], window['high'].iloc[-1], window['low'].iloc[-1], window['close'].iloc[-1]
    corpo = fe - ab
    pavio_sup = mx - max(ab, fe)
    pavio_inf = min(ab, fe) - mn
    faixa_total = (mx - mn) + 1e-9
    
    direcao_bio = (corpo / faixa_total) * 100
    pressao_rejeicao = ((pavio_sup + pavio_inf) / faixa_total) * 100

    # --- MUSCULATURA ESTATÍSTICA (Z-Score com Scikit-Learn) ---
    precos = window['close'].values.reshape(-1, 1)
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(precos)
    z_atual = float(z_scores[-1][0])
    
    # Score de Prontidão (0 a 100%)
    score_prontidao = min(abs(z_atual) / 2.0, 1.0) * 100
    atr = (window['high'] - window['low']).mean()

    res = {
        "tipo": None, "score": score_prontidao, "direcao": direcao_bio, 
        "pressao": pressao_rejeicao, "z_inf": p_atual - (atr * 0.2), "z_sup": p_atual + (atr * 0.2)
    }

    # Gatilho de Operação Institucional
    if abs(z_atual) > 1.5:
        res["tipo"] = "COMPRA" if z_atual > 0 else "VENDA"
        mult = {"SCALPER": 1.5, "DAY": 2.5, "SWING": 4.0, "POSITION": 6.0}[modo]
        direcao_m = 1 if res["tipo"] == "COMPRA" else -1
        
        res.update({
            "tp": [p_atual + (atr * mult * direcao_m), p_atual + (atr * mult * 1.6 * direcao_m)],
            "sl": [p_atual - (atr * mult * 0.8 * direcao_m), p_atual - (atr * mult * 1.2 * direcao_m)]
        })
    return res
