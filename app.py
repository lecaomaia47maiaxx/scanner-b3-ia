import yfinance as yf
import time
import logging
from telegram import Bot

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

TOKEN = "8759794487:AAH9Roaz5gxMw7F5lXLJ7aL2DeXWmi5gQU8"
CHAT_ID = "8759794487"

bot = Bot(token=TOKEN)

print("ROBÔ GLOBAL INICIADO")

# AÇÕES ESTÁVEIS DA B3
acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA","WEGE3.SA",
"RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA","RADL3.SA","RAIL3.SA",
"B3SA3.SA","GGBR4.SA","USIM5.SA","CSNA3.SA","MGLU3.SA","CMIG4.SA",
"EQTL3.SA","SBSP3.SA","VBBR3.SA","UGPA3.SA","HAPV3.SA","TIMS3.SA"
]

# INDICES GLOBAIS
indices = {
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOWJONES":"^DJI",
"NIKKEI":"^N225",
"DAX":"^GDAXI"
}

bitcoin = "BTC-USD"


def sentimento(valor):

    if valor > 0.5:
        return "ALTISTA 🟢"

    if valor < -0.5:
        return "BAIXISTA 🔴"

    return "NEUTRO ⚪"


def analisar_indices():

    texto = ""
    soma = 0
    cont = 0

    for nome,ticker in indices.items():

        try:

            df = yf.download(
                ticker,
                period="2d",
                progress=False,
                threads=False
            )

            if df.empty:
                continue

            atual = df["Close"].iloc[-1]
            anterior = df["Close"].iloc[-2]

            variacao = (atual-anterior)/anterior*100

            soma += variacao
            cont += 1

            texto += f"{nome}: {round(variacao,2)}%\n"

        except:
            pass

    if cont == 0:
        return "Sem dados\n"

    media = soma/cont

    texto += f"\nSentimento geral: {sentimento(media)}\n"

    return texto


def analisar_bitcoin():

    try:

        df = yf.download(
            bitcoin,
            period="2d",
            progress=False,
            threads=False
        )

        if df.empty:
            return "Bitcoin sem dados\n"

        atual = df["Close"].iloc[-1]
        anterior = df["Close"].iloc[-2]

        var = (atual-anterior)/anterior*100

        return f"Bitcoin: ${round(atual,2)} ({round(var,2)}%)\n"

    except:

        return "Bitcoin sem dados\n"


def detectar_acumulacao(df):

    try:

        volume = df["Volume"]
        media = volume.rolling(20).mean()

        if volume.iloc[-1] > media.iloc[-1]*1.7:
            return True

        return False

    except:
        return False


def analisar_acao(ticker):

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

        atual = preco.iloc[-1]
        anterior = preco.iloc[-2]

        queda = (atual-anterior)/anterior*100

        if queda > -0.7:
            return None

        acumulacao = detectar_acumulacao(df)

        prob = abs(queda)*10

        if acumulacao:
            prob += 25

        return {
            "acao":ticker.replace(".SA",""),
            "preco":round(atual,2),
            "prob":round(prob,1)
        }

    except:
        return None


def scanner_b3():

    sinais = []

    for acao in acoes:

        r = analisar_acao(acao)

        if r:
            sinais.append(r)

    sinais = sorted(sinais,key=lambda x:x["prob"],reverse=True)

    return sinais[:5]


while True:

    try:

        print("Gerando relatório...")

        msg = "🌎 RELATÓRIO GLOBAL\n\n"

        msg += "📊 ÍNDICES GLOBAIS\n"
        msg += analisar_indices()

        msg += "\n₿ BITCOIN\n"
        msg += analisar_bitcoin()

        sinais = scanner_b3()

        if sinais:

            msg += "\n📈 OPORTUNIDADES B3\n\n"

            for s in sinais:

                msg += f"{s['acao']} | Preço {s['preco']} | Prob {s['prob']}%\n"

        else:

            msg += "\nSem oportunidades na B3 agora\n"

        bot.send_message(chat_id=CHAT_ID,text=msg)

        print("Relatório enviado")

    except Exception as e:

        print("Erro:",e)

    time.sleep(600)
