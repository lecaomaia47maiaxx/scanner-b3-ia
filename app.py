import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time
from telegram import Bot

# CONFIGURAR TELEGRAM
TOKEN = "8675758808:AAEhsr9A0HwFazy92GFUndyh2oSJFEhlMEE"
CHAT_ID = "8675758808"

bot = Bot(token=TOKEN)

print("ROBÔ B3 INICIADO")

# AÇÕES PRINCIPAIS DA B3
acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA",
"JBSS3.SA","RADL3.SA","RAIL3.SA","HAPV3.SA","B3SA3.SA"
]

def mercado_aberto():

    agora = datetime.datetime.now()

    return agora.hour >= 10 and agora.hour <= 17


def analisar_acao(ticker):

    df = yf.download(ticker, period="1y", interval="1d")

    if len(df) < 30:
        return None

    df["retorno"] = df["Close"].pct_change()*100

    hoje = df.iloc[-1]

    queda = hoje["retorno"]

    if queda > -1.5:
        return None

    historico = df[df["retorno"] <= queda]

    if len(historico) < 5:
        return None

    reversao = (historico["Close"].shift(-1) > historico["Close"]).mean()

    preco = hoje["Close"]

    alvo = preco * 1.02
    stop = preco * 0.98

    return {
        "acao":ticker.replace(".SA",""),
        "preco":round(preco,2),
        "queda":round(queda,2),
        "prob":round(reversao*100,1),
        "alvo":round(alvo,2),
        "stop":round(stop,2)
    }


def escanear():

    oportunidades = []

    for acao in acoes:

        try:

            r = analisar_acao(acao)

            if r and r["prob"] > 60:

                oportunidades.append(r)

        except:
            pass

    oportunidades = sorted(
        oportunidades,
        key=lambda x:x["prob"],
        reverse=True
    )

    return oportunidades[:10]


while True:

    if mercado_aberto():

        lista = escanear()

        if lista:

            msg = "📊 OPORTUNIDADES B3\n\n"

            for a in lista:

                msg += f"""
{a['acao']}

Preço atual: {a['preco']}
Queda: {a['queda']}%

Entrada: {a['preco']}
Venda: {a['alvo']}
Stop: {a['stop']}

Probabilidade: {a['prob']}%

------------------
"""

            bot.send_message(chat_id=CHAT_ID,text=msg)

            print("Sinal enviado")

    else:

        print("Aguardando mercado abrir...")

    time.sleep(600)
