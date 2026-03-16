import time
import requests
import yfinance as yf
import pandas as pd
import ta

# ==============================
# CONFIGURAÇÕES TELEGRAM
# ==============================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# ==============================
# LISTA DE AÇÕES DA B3
# ==============================

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

# ==============================
# ENVIAR MENSAGEM TELEGRAM
# ==============================

def enviar_telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url, data=payload)

    except Exception as erro:
        print("Erro ao enviar Telegram:", erro)


# ==============================
# ANALISAR AÇÃO
# ==============================

def analisar_acao(ticker):

    try:

        dados = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False
        )

        if dados.empty:
            return f"{ticker} sem dados"

        # Corrige erro de dimensão
        close = dados["Close"].squeeze()

        rsi = ta.momentum.RSIIndicator(close).rsi()

        rsi_atual = rsi.iloc[-1]

        if rsi_atual < 30:
            sinal = "🟢 POSSÍVEL COMPRA"

        elif rsi_atual > 70:
            sinal = "🔴 POSSÍVEL VENDA"

        else:
            sinal = "⚪ NEUTRO"

        return f"{ticker} | RSI {round(rsi_atual,2)} | {sinal}"

    except Exception as erro:

        return f"{ticker} erro na análise"


# ==============================
# GERAR RELATÓRIO
# ==============================

def gerar_relatorio():

    relatorio = "📊 RELATÓRIO AUTOMÁTICO B3\n\n"

    for acao in acoes:

        resultado = analisar_acao(acao)

        relatorio += resultado + "\n"

    return relatorio


# ==============================
# LOOP PRINCIPAL DO ROBÔ
# ==============================

print("Robô iniciado...")

while True:

    try:

        relatorio = gerar_relatorio()

        print(relatorio)

        enviar_telegram(relatorio)

        print("Relatório enviado para Telegram")

    except Exception as erro:

        print("Erro geral:", erro)

    # espera 30 minutos
    time.sleep(1800)
