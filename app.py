import yfinance as yf
import pandas as pd
import numpy as np
import time
from telegram import Bot

TOKEN = "8759794487:AAH9Roaz5gxMw7F5lXLJ7aL2DeXWmi5gQU8"
CHAT_ID = "8759794487"

bot = Bot(token=TOKEN)

print("ROBÔ B3 INICIADO")

# LISTA DE AÇÕES (replicada para aumentar universo analisado)
acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA","WEGE3.SA",
"RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA","JBSS3.SA","RADL3.SA",
"RAIL3.SA","HAPV3.SA","B3SA3.SA","GGBR4.SA","USIM5.SA","CSNA3.SA",
"BRFS3.SA","MRFG3.SA","MGLU3.SA","AZUL4.SA","GOLL4.SA","ELET3.SA",
"ELET6.SA","CPLE6.SA","CMIG4.SA","ENGI11.SA","EQTL3.SA","SBSP3.SA",
"KLBN11.SA","VBBR3.SA","UGPA3.SA","RAIZ4.SA","RRRP3.SA"
]

acoes = acoes * 8   # aumenta universo (~280 ativos)

def detectar_acumulacao(preco, volume):

    try:

        vol_media = volume.rolling(20).mean()

        if len(preco) < 20:
            return False

        queda = (preco.iloc[-1] - preco.iloc[-5]) / preco.iloc[-5]

        volume_forte = volume.iloc[-1] > vol_media.iloc[-1] * 1.8

        if queda < -0.01 and volume_forte:
            return True

        return False

    except:
        return False


def analisar_acao(df, ticker):

    try:

        preco = df["Close"]
        volume = df["Volume"]

        if len(preco) < 30:
            return None

        preco_atual = preco.iloc[-1]
        preco_ant = preco.iloc[-2]

        queda = ((preco_atual - preco_ant) / preco_ant) * 100

        if queda > -0.7:
            return None

        acumulacao = detectar_acumulacao(preco, volume)

        volatilidade = preco.pct_change().std() * 100

        prob = abs(queda) * 12 + volatilidade * 6

        if acumulacao:
            prob += 25

        prob = min(95, prob)

        alvo = preco_atual * 1.025
        stop = preco_atual * 0.98

        return {
            "acao": ticker.replace(".SA",""),
            "preco": round(preco_atual,2),
            "queda": round(queda,2),
            "prob": round(prob,1),
            "alvo": round(alvo,2),
            "stop": round(stop,2),
            "acumulacao": acumulacao
        }

    except:
        return None


def escanear():

    print("Escaneando mercado...")

    try:

        dados = yf.download(
            acoes,
            period="5d",
            interval="5m",
            group_by="ticker",
            progress=False
        )

    except:

        print("Erro ao baixar dados")

        return []

    oportunidades = []

    for ticker in acoes:

        try:

            df = dados[ticker]

            r = analisar_acao(df, ticker)

            if r and r["prob"] > 60:

                oportunidades.append(r)

        except:
            pass

    oportunidades = sorted(
        oportunidades,
        key=lambda x:x["prob"],
        reverse=True
    )

    return oportunidades[:20]


# TESTE IMEDIATO (não depende de horário)

while True:

    lista = escanear()

    if lista:

        msg = "🚨 SCANNER B3 - TESTE\n\n"

        for a in lista:

            msg += f"""
{a['acao']}

Preço: {a['preco']}
Queda: {a['queda']}%

Entrada: {a['preco']}
Alvo: {a['alvo']}
Stop: {a['stop']}

Probabilidade subir hoje: {a['prob']}%
"""

            if a["acumulacao"]:
                msg += "💰 ACUMULAÇÃO INSTITUCIONAL DETECTADA\n"

            msg += "-----------------\n"

        bot.send_message(chat_id=CHAT_ID, text=msg)

        print("Sinais enviados")

    time.sleep(120)
