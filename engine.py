import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler

def obter_dados_institucionais(ticker="EURUSD=X"):
    try:
        # Puxa 1 mês de dados em intervalos de 15min para musculatura estatística
        data = yf.download(ticker, period="1mo", interval="15m", progress=False)
        if data.empty: return pd.DataFrame(), 0.0
        
        # Correção Crítica: Extração segura de valores únicos (evita FutureWarning)
        p_atual = float(data['Close'].iloc[-1].iloc[0]) if isinstance(data['Close'].iloc[-1], pd.Series) else float(data['Close'].iloc[-1])
        
        # Dados diários para cálculo de Pips
        dados_diarios = yf.download(ticker, period="2d", interval="1d", progress=False)
        p_ontem = float(dados_diarios['Close'].iloc[-2])
        pips_diff = (p_atual - p_ontem) * 10000
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        return df, float(pips_diff)
    except Exception as e:
        print(f"Erro na coleta: {e}")
        return pd.DataFrame(), 0.0

def motor_auraxis_v15(df, modo="DAY"):
    # Janelas de observação conforme o perfil
    janelas = {"SCALPER": 15, "DAY": 35, "SWING": 75, "POSITION": 150}
    p = janelas.get(modo, 35)
    
    # Seleciona a janela de tempo
    window = df.tail(p).copy()
    p_atual = float(window['close'].iloc[-1].iloc[0]) if isinstance(window['close'].iloc[-1], pd.Series) else float(window['close'].iloc[-1])
    
    # --- BIOMETRIA DO CANDLE ---
    # Extração dos componentes para cálculo de Direção e Pressão
    ab = window['open'].iloc[-1]
    mx = window['high'].iloc[-1]
    mn = window['low'].iloc[-1]
    fe = window['close'].iloc[-1]
    
    corpo = fe - ab
    pavio_sup = mx - max(ab, fe)
    pavio_inf = min(ab, fe) - mn
    faixa_total = (mx - mn) + 1e-9 # Evita divisão por zero
    
    direcao_bio = (corpo / faixa_total) * 100
    pressao_rejeicao = ((pavio_sup + pavio_inf) / faixa_total) * 100

    # --- CÁLCULO DE Z-SCORE (Scikit-Learn) ---
    # Transforma o preço em desvio padrão para identificar exaustão
    precos = window['close'].values.reshape(-1, 1)
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(precos)
    z_atual = float(z_scores[-1][0])
    
    # Score de Prontidão: Quanto mais longe da média, maior o score (max 100)
    score_prontidao = min(abs(z_atual) / 2.0, 1.0) * 100
    atr = (window['high'] - window['low']).mean()

    res = {
        "tipo": None, 
        "score": float(score_prontidao), 
        "direcao": float(direcao_bio), 
        "pressao": float(pressao_rejeicao), 
        "z_inf": p_atual - (atr * 0.2), 
        "z_sup": p_atual + (atr * 0.2)
    }

    # Gatilho Institucional: Z-Score acima de 1.5 indica desequilíbrio
    if abs(z_atual) > 1.5:
        res["tipo"] = "COMPRA" if z_atual > 0 else "VENDA"
        # Multiplicador de alvo baseado no perfil
        mult = {"SCALPER": 1.5, "DAY": 2.5, "SWING": 4.0, "POSITION": 6.0}[modo]
        direcao_m = 1 if res["tipo"] == "COMPRA" else -1
        
        res.update({
            "tp": [p_atual + (atr * mult * direcao_m)],
            "sl": [p_atual - (atr * mult * 0.8 * direcao_m)]
        })
        
    return res
