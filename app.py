import time
import requests
import yfinance as yf
import pandas as pd
import ta

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

acoes = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "ABEV3.SA",
    "WEGE3.SA",
    "BBAS3.SA",
    "B3SA3.SA",
    "JBSS3.SA",
    "PETR3.SA"
]


def enviar_telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


def analisar_acao(ticker):

    dados = yf.download(ticker, period="3mo", interval="1d")

    if dados.empty:
        return f"{ticker} sem dados"

    dados["RSI"] = ta.momentum.RSIIndicator(
        dados["Close"]).rsi()

    rsi = dados["RSI"].iloc[-1]

    if rsi < 30:
        sinal = "🟢 POSSÍVEL COMPRA"

    elif rsi > 70:
        sinal = "🔴 POSSÍVEL VENDA"

    else:
        sinal = "⚪ NEUTRO"

    return f"{ticker} | RSI {round(rsi,2)} | {sinal}"


def gerar_relatorio():

    relatorio = "📊 RELATÓRIO B3\n\n"

    for acao in acoes:

        resultado = analisar_acao(acao)

        relatorio += resultado + "\n"

    return relatorio


while True:

    try:

        relatorio = gerar_relatorio()

        enviar_telegram(relatorio)

        print("Relatório enviado")

    except Exception as e:

        print("Erro:", e)

    time.sleep(1800)
