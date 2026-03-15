import yfinance as yf
import pandas as pd
import numpy as np
import time
from telegram import Bot

TOKEN = "8759794487:AAH9Roaz5gxMw7F5lXLJ7aL2DeXWmi5gQU8"
CHAT_ID = "8759794487"

bot = Bot(token=TOKEN)

print("ROBÔ B3 INICIADO")

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA","WEGE3.SA",
"RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA","RADL3.SA","RAIL3.SA",
"HAPV3.SA","B3SA3.SA","GGBR4.SA","USIM5.SA","CSNA3.SA","MGLU3.SA",
"CMIG4.SA","ENGI11.SA","EQTL3.SA","SBSP3.SA","KLBN11.SA","VBBR3.SA",
"UGPA3.SA","RAIZ4.SA"
]

def detectar_acumulacao(df):

    try:

        preco = df["Close"]
        volume = df["Volume"]

        vol_media = volume.rolling(20).mean()

        queda = (preco.iloc[-1] - preco.iloc[-5]) / preco.iloc[-5]

        volume_forte = volume.iloc[-1] > vol_media.iloc[-1] * 1.7

        if queda < -0.01 and volume_forte:
            return True

        return False

    except:
        return False


def analisar(ticker):

    try:

        df = yf.download(
            ticker,
            period="5d",
            interval="5m",
            progress=False,
            threads=False
        )

        if df.empty:
            return None

        preco = df["Close"]

        preco_atual = preco.iloc[-1]
        preco_ant = preco.iloc[-2]

        queda = ((preco_atual - preco_ant) / preco_ant) * 100

        if queda > -0.7:
            return None

        acumulacao = detectar_acumulacao(df)

        volatilidade = preco.pct_change().std()*100

        prob = abs(queda)*10 + volatilidade*5

        if acumulacao:
            prob += 20

        prob = min(90, prob)

        alvo = preco_atual * 1.02
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


while True:

    try:

        print("Escaneando mercado...")

        oportunidades = []

        for ticker in acoes:

            r = analisar(ticker)

            if r and r["prob"] > 60:

                oportunidades.append(r)

        oportunidades = sorted(
            oportunidades,
            key=lambda x: x["prob"],
            reverse=True
        )

        oportunidades = oportunidades[:10]

        if oportunidades:

            msg = "🚨 SCANNER B3\n\n"

            for a in oportunidades:

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
                    msg += "💰 Acumulação institucional detectada\n"

                msg += "-----------------\n"

            bot.send_message(chat_id=CHAT_ID, text=msg)

            print("Sinais enviados")

        else:

            print("Nenhuma oportunidade encontrada")

    except Exception as e:

        print("Erro no ciclo:", e)

    time.sleep(180)
