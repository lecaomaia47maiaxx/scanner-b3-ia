import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# =====================================
# TELEGRAM
# =====================================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# =====================================
# AÇÕES MAIS LÍQUIDAS B3
# =====================================

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA",
"ABEV3.SA","BBAS3.SA","WEGE3.SA","B3SA3.SA",
"JBSS3.SA","RENT3.SA","LREN3.SA","PRIO3.SA",
"SUZB3.SA","RADL3.SA","RAIL3.SA"
]

# =====================================
# ENVIAR TELEGRAM
# =====================================

def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url,data=payload)
    except:
        print("erro telegram")

# =====================================
# ANALISE ESTATISTICA
# =====================================

def analisar_acao(ticker):

    try:

        dados = yf.download(
            ticker,
            period="10y",
            interval="1d",
            progress=False
        )

        if len(dados) < 200:
            return None

        close = dados["Close"]

        # retorno 5 dias
        retorno = close.pct_change(5)

        queda_atual = retorno.iloc[-1]

        if queda_atual > -0.03:
            return None

        historico = retorno.dropna()

        # encontrar quedas parecidas
        semelhantes = historico[
            (historico < queda_atual * 1.2) &
            (historico > queda_atual * 0.8)
        ]

        if len(semelhantes) < 5:
            return None

        subidas = 0

        for i in semelhantes.index:

            pos = dados.index.get_loc(i)

            if pos + 5 < len(close):

                futuro = close.iloc[pos+5]

                atual = close.iloc[pos]

                if futuro > atual:
                    subidas += 1

        prob = subidas / len(semelhantes)

        if prob > 0.6:

            return f"""
📈 POSSÍVEL REVERSÃO

Ação: {ticker}

queda recente: {round(queda_atual*100,2)}%

ocorrências históricas: {len(semelhantes)}

probabilidade de alta: {round(prob*100,1)}%
"""

    except:

        return None


# =====================================
# GERAR RELATÓRIO
# =====================================

def gerar_relatorio():

    sinais = []

    for acao in acoes:

        resultado = analisar_acao(acao)

        if resultado:

            sinais.append(resultado)

    if not sinais:

        return "📊 Nenhuma reversão estatística encontrada hoje"

    msg = "📊 SINAIS ESTATÍSTICOS B3\n\n"

    for s in sinais:

        msg += s + "\n"

    return msg


# =====================================
# LOOP DO ROBÔ
# =====================================

print("robô estatístico iniciado")

while True:

    try:

        relatorio = gerar_relatorio()

        print(relatorio)

        enviar(relatorio)

    except Exception as e:

        print("erro:",e)

    time.sleep(3600)
