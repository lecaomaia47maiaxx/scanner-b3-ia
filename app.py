import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time
from telegram import Bot

TOKEN = "8675758808:AAEhsr9A0HwFazy92GFUndyh2oSJFEhlMEE"
CHAT_ID = "8675758808"

bot = Bot(token=TOKEN)

print("ROBÔ B3 INICIADO")

# LISTA GRANDE DE AÇÕES DA B3 (exemplo grande)
acoes = [
"ABEV3.SA","ALPA4.SA","AMER3.SA","ASAI3.SA","AZUL4.SA","B3SA3.SA","BBAS3.SA",
"BBDC3.SA","BBDC4.SA","BBSE3.SA","BEEF3.SA","BPAC11.SA","BRAP4.SA","BRFS3.SA",
"BRKM5.SA","CCRO3.SA","CIEL3.SA","CMIG4.SA","COGN3.SA","CPFE3.SA","CPLE6.SA",
"CRFB3.SA","CSAN3.SA","CSNA3.SA","CVCB3.SA","CYRE3.SA","DXCO3.SA","ECOR3.SA",
"ELET3.SA","ELET6.SA","EMBR3.SA","ENEV3.SA","ENGI11.SA","EQTL3.SA","EZTC3.SA",
"FLRY3.SA","GGBR4.SA","GOAU4.SA","GOLL4.SA","HAPV3.SA","HYPE3.SA","IGTI11.SA",
"IRBR3.SA","ITSA4.SA","ITUB4.SA","JBSS3.SA","KLBN11.SA","LREN3.SA","MGLU3.SA",
"MRFG3.SA","MRVE3.SA","MULT3.SA","NTCO3.SA","PCAR3.SA","PETR3.SA","PETR4.SA",
"PRIO3.SA","QUAL3.SA","RADL3.SA","RAIL3.SA","RAIZ4.SA","RENT3.SA","RRRP3.SA",
"SANB11.SA","SBSP3.SA","SLCE3.SA","SMTO3.SA","SUZB3.SA","TAEE11.SA","TIMS3.SA",
"TOTS3.SA","UGPA3.SA","USIM5.SA","VALE3.SA","VBBR3.SA","WEGE3.SA","YDUQ3.SA"
]

# duplicamos para aumentar universo (~300)
acoes = acoes * 4


def mercado_aberto():

    agora = datetime.datetime.now()

    return agora.hour >= 10 and agora.hour <= 17


def analisar_acao(df, ticker):

    try:

        if ticker not in df.columns:
            return None

        dados = df[ticker].dropna()

        if len(dados) < 20:
            return None

        preco = dados.iloc[-1]
        preco_ant = dados.iloc[-2]

        queda = ((preco - preco_ant) / preco_ant) * 100

        if queda > -1:
            return None

        volatilidade = dados.pct_change().std()*100

        prob = min(90, max(50, abs(queda)*10 + volatilidade*5))

        alvo = preco * 1.02
        stop = preco * 0.98

        return {
            "acao": ticker.replace(".SA",""),
            "preco": round(preco,2),
            "queda": round(queda,2),
            "prob": round(prob,1),
            "alvo": round(alvo,2),
            "stop": round(stop,2)
        }

    except:

        return None


def escanear():

    try:

        dados = yf.download(
            acoes,
            period="5d",
            interval="5m",
            group_by='ticker',
            progress=False
        )

    except:

        return []

    oportunidades = []

    for ticker in acoes:

        try:

            df = dados[ticker]

            r = analisar_acao(df["Close"], ticker)

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


while True:

    if mercado_aberto():

        print("Escaneando mercado...")

        lista = escanear()

        if lista:

            msg = "📊 TOP OPORTUNIDADES B3\n\n"

            for a in lista:

                msg += f"""
{a['acao']}

Preço: {a['preco']}
Queda: {a['queda']}%

Entrada: {a['preco']}
Alvo: {a['alvo']}
Stop: {a['stop']}

Probabilidade subir hoje: {a['prob']}%

-------------------
"""

            bot.send_message(chat_id=CHAT_ID,text=msg)

            print("Sinais enviados")

    else:

        print("Aguardando mercado abrir")

    time.sleep(60)
