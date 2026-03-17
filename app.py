import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser

# =========================
# TELEGRAM
# =========================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# =========================
# AÇÕES LÍQUIDAS B3
# =========================

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","ABEV3.SA",
"BBAS3.SA","WEGE3.SA","B3SA3.SA","JBSS3.SA","RENT3.SA",
"LREN3.SA","PRIO3.SA","SUZB3.SA","RADL3.SA","RAIL3.SA",
"GGBR4.SA","CSNA3.SA","USIM5.SA","EQTL3.SA","VIVT3.SA"
]

# =========================
# TELEGRAM
# =========================

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


# =========================
# CALCULAR RSI
# =========================

def calcular_rsi(close,periodo=14):

    delta = close.diff()

    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(periodo).mean()
    media_perda = perda.rolling(periodo).mean()

    rs = media_ganho / media_perda

    rsi = 100 - (100/(1+rs))

    return rsi


# =========================
# ANALISE QUANTITATIVA
# =========================

def analisar_acao(ticker):

    try:

        dados = yf.download(
            ticker,
            period="10y",
            interval="1d",
            progress=False
        )

        close = dados["Close"].squeeze()

        retorno5 = close.pct_change(5)

        queda_atual = retorno5.iloc[-1]

        rsi = calcular_rsi(close)

        rsi_atual = rsi.iloc[-1]

        historico = retorno5.dropna()

        semelhantes = historico[
            (historico < queda_atual*1.2) &
            (historico > queda_atual*0.8)
        ]

        if len(semelhantes) < 5:
            prob = 0
        else:

            subidas = 0

            for i in semelhantes.index:

                pos = dados.index.get_loc(i)

                if pos+5 < len(close):

                    if close.iloc[pos+5] > close.iloc[pos]:

                        subidas += 1

            prob = subidas/len(semelhantes)

        # força da queda
        forca = abs(queda_atual)

        # fator RSI
        fator_rsi = max(0,(50-rsi_atual)/50)

        score = (prob*0.5)+(forca*0.3)+(fator_rsi*0.2)

        return {
            "acao": ticker.replace(".SA",""),
            "queda": queda_atual,
            "prob": prob,
            "rsi": rsi_atual,
            "score": score
        }

    except:

        return None


# =========================
# ANALISE DO MERCADO
# =========================

def analisar_mercado():

    resultados = []

    alertas = []

    for acao in acoes:

        r = analisar_acao(acao)

        if r:

            resultados.append(r)

            if r["prob"] > 0.65 and r["rsi"] < 40:

                alertas.append(r)

    df = pd.DataFrame(resultados)

    df = df.sort_values("score",ascending=False)

    top = df.head(10)

    msg = "📊 RANKING OPORTUNIDADES B3\n\n"

    for i,row in top.iterrows():

        cor = "🟢"

        if row["queda"] > 0:
            cor = "🟢"

        elif row["queda"] < -0.03:
            cor = "🔴"

        else:
            cor = "🟡"

        msg += (
        f"{cor} {row['acao']} "
        f"queda {round(row['queda']*100,2)}% "
        f"prob {round(row['prob']*100,1)}% "
        f"RSI {round(row['rsi'],1)} "
        f"score {round(row['score'],2)}\n"
        )

    # ALERTAS FORTES

    if alertas:

        msg += "\n🚨 ALERTAS FORTES\n\n"

        for a in alertas:

            msg += (
            f"🟢 POSSÍVEL REVERSÃO\n"
            f"{a['acao']}\n"
            f"queda {round(a['queda']*100,2)}%\n"
            f"prob {round(a['prob']*100,1)}%\n"
            f"RSI {round(a['rsi'],1)}\n\n"
            )

    return msg


# =========================
# NOTÍCIAS EM PORTUGUÊS
# =========================

def noticias():

    feeds = [
    "https://www.infomoney.com.br/feed/",
    "https://br.investing.com/rss/news_25.rss"
    ]

    lista = []

    for feed in feeds:

        try:

            data = feedparser.parse(feed)

            for item in data.entries[:3]:

                lista.append(item.title)

        except:
            pass

    msg = "\n📰 NOTÍCIAS DO MERCADO\n\n"

    for n in lista[:5]:

        msg += f"- {n}\n"

    return msg


# =========================
# RELATORIO FINAL
# =========================

def relatorio():

    mercado = analisar_mercado()

    news = noticias()

    return mercado + news


# =========================
# LOOP
# =========================

print("Robô quantitativo iniciado")

while True:

    try:

        mensagem = relatorio()

        print(mensagem)

        enviar(mensagem)

    except Exception as e:

        print("erro:",e)

    time.sleep(3600)
