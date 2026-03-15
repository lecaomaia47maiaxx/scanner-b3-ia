import yfinance as yf
import time
import requests

TOKEN = "8759794487:AAH9Roaz5gxMw7F5lXLJ7aL2DeXWmi5gQU8"
CHAT_ID = "8759794487"

def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        print("Erro ao enviar mensagem")


print("ROBÔ GLOBAL INICIADO")

# aviso inicial
enviar("🤖 Robô iniciado com sucesso")

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA",
"RADL3.SA","RAIL3.SA","B3SA3.SA","GGBR4.SA","USIM5.SA",
"CSNA3.SA","MGLU3.SA","CMIG4.SA","EQTL3.SA","SBSP3.SA"
]

indices = {
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOW":"^DJI",
"NIKKEI":"^N225",
"DAX":"^GDAXI"
}

bitcoin = "BTC-USD"


def analisar_indices():

    texto = ""
    soma = 0
    cont = 0

    for nome,ticker in indices.items():

        try:

            df = yf.download(
                ticker,
                period="2d",
                progress=False
            )

            if df.empty:
                continue

            close = df["Close"]

            if len(close) < 2:
                continue

            atual = float(close.iloc[-1])
            anterior = float(close.iloc[-2])

            variacao = (atual-anterior)/anterior*100

            soma += variacao
            cont += 1

            texto += f"{nome}: {round(variacao,2)}%\n"

        except:
            continue

    if cont == 0:
        return "Sem dados\n"

    media = soma/cont

    if media > 0.5:
        sentimento = "ALTISTA 🟢"
    elif media < -0.5:
        sentimento = "BAIXISTA 🔴"
    else:
        sentimento = "NEUTRO ⚪"

    texto += f"\nSentimento global: {sentimento}\n"

    return texto


def analisar_bitcoin():

    try:

        df = yf.download(
            bitcoin,
            period="2d",
            progress=False
        )

        if df.empty:
            return "Bitcoin sem dados\n"

        close = df["Close"]

        atual = float(close.iloc[-1])
        anterior = float(close.iloc[-2])

        variacao = (atual-anterior)/anterior*100

        return f"Bitcoin: ${round(atual,2)} ({round(variacao,2)}%)\n"

    except:
        return "Bitcoin sem dados\n"


def detectar_acumulacao(df):

    try:

        volume = df["Volume"]

        if len(volume) < 20:
            return False

        media = volume.rolling(20).mean()

        v_atual = float(volume.iloc[-1])
        v_media = float(media.iloc[-1])

        if v_atual > v_media*1.7:
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
            progress=False
        )

        if df.empty:
            return None

        close = df["Close"]

        if len(close) < 3:
            return None

        atual = float(close.iloc[-1])
        anterior = float(close.iloc[-2])

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

    sinais = sorted(
        sinais,
        key=lambda x:x["prob"],
        reverse=True
    )

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

        enviar(msg)

        print("Relatório enviado")

    except Exception as e:

        print("Erro:", e)

    time.sleep(600)
