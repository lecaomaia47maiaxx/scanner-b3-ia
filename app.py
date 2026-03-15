import os
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Bot
from telegram.ext import Updater
from datetime import datetime

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

# ==============================
# FUNÇÃO RSI
# ==============================
def calcular_rsi(series, periodo=14):
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(window=periodo).mean()
    media_perda = perda.rolling(window=periodo).mean()

    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))

    return rsi


# ==============================
# FUNÇÃO DE ANÁLISE
# ==============================
def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d")

        if df.empty:
            return f"{ticker} → Sem dados disponíveis"

        close = df["Close"].squeeze()

        df["RSI"] = calcular_rsi(close)
        df["MM9"] = close.rolling(9).mean()
        df["MM21"] = close.rolling(21).mean()

        preco = close.iloc[-1]
        rsi = df["RSI"].iloc[-1]
        mm9 = df["MM9"].iloc[-1]
        mm21 = df["MM21"].iloc[-1]

        # Classificação RSI
        if rsi < 30:
            status_rsi = "Sobrevendido"
        elif rsi > 70:
            status_rsi = "Sobrecomprado"
        else:
            status_rsi = "Neutro"

        # Geração de sinal
        if rsi < 30 and mm9 > mm21:
            sinal = "🟢 FORTE COMPRA"
        elif rsi > 70 and mm9 < mm21:
            sinal = "🔴 FORTE VENDA"
        elif mm9 > mm21:
            sinal = "🟡 TENDÊNCIA DE ALTA"
        elif mm9 < mm21:
            sinal = "🟡 TENDÊNCIA DE BAIXA"
        else:
            sinal = "⚪ NEUTRO"

        mensagem = (
            f"📈 {ticker.replace('.SA','')}\n"
            f"Preço: R$ {preco:.2f}\n"
            f"RSI: {rsi:.2f} ({status_rsi})\n"
            f"MM9: {mm9:.2f}\n"
            f"MM21: {mm21:.2f}\n"
            f"👉 SINAL: {sinal}\n"
        )

        return mensagem

    except Exception as e:
        return f"{ticker} → Erro: {str(e)}"


# ==============================
# MERCADO GLOBAL
# ==============================
def analisar_mercado_global():
    indices = {
        "🇺🇸 S&P 500": "^GSPC",
        "🇺🇸 NASDAQ": "^IXIC",
        "🇺🇸 DOW JONES": "^DJI",
        "🇪🇺 EURO STOXX": "^STOXX50E",
        "🇨🇳 SHANGHAI": "000001.SS"
    }

    resultado = "\n🌎 MERCADO GLOBAL\n\n"

    for nome, ticker in indices.items():
        try:
            df = yf.download(ticker, period="5d", interval="1d")
            close = df["Close"].squeeze()

            variacao = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

            if variacao > 0:
                tendencia = "🟢 Alta"
            else:
                tendencia = "🔴 Baixa"

            resultado += f"{nome}: {variacao:.2f}% ({tendencia})\n"

        except:
            resultado += f"{nome}: erro\n"

    return resultado


# ==============================
# RELATÓRIO COMPLETO
# ==============================
def enviar_relatorio():
    ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]

    mensagem = f"📊 RELATÓRIO B3\n{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

    for ativo in ativos:
        mensagem += analisar_ativo(ativo) + "\n"

    mensagem += analisar_mercado_global()

    bot.send_message(chat_id=CHAT_ID, text=mensagem)


# ==============================
# EXECUÇÃO
# ==============================
if __name__ == "__main__":
    print("Bot rodando...")
    enviar_relatorio()
