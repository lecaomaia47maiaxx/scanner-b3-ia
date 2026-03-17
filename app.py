import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser

# ==============================
# TELEGRAM
# ==============================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# ==============================
# AÇÕES MAIS LÍQUIDAS
# ==============================

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","ABEV3.SA",
"BBAS3.SA","WEGE3.SA","B3SA3.SA","JBSS3.SA","RENT3.SA",
"LREN3.SA","PRIO3.SA","SUZB3.SA","RADL3.SA","RAIL3.SA",
"GGBR4.SA","CSNA3.SA","USIM5.SA","EQTL3.SA","VIVT3.SA"
]

# ==============================
# TELEGRAM
# ==============================

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

# ==============================
# ANALISE ESTATÍSTICA
# ==============================

def analisar_acao(ticker):

    try:

        dados = yf.download(
            ticker,
            period="10y",
            interval="1d",
            progress=False
        )

        if len(dados) < 300:
            return None

        close = dados["Close"].squeeze()

        retorno5 = close.pct_change(5)

        queda_atual = retorno5.iloc[-1]

        historico = retorno5.dropna()

        semelhantes = historico[
            (historico < queda_atual * 1.2) &
            (historico > queda_atual * 0.8)
        ]

        if len(semelhantes) < 5:
            prob = 0
        else:

            subidas = 0

            for i in semelhantes.index:

                pos = dados.index.get_loc(i)

                if pos + 5 < len(close):

                    if close.iloc[pos+5] > close.iloc[pos]:
                        subidas += 1

            prob = subidas / len(semelhantes)

        score = prob * abs(queda_atual)

        return {
            "acao": ticker.replace(".SA",""),
            "queda": queda_atual,
            "prob": prob,
            "score": score
        }

    except:
        return None


# ==============================
# GERAR LISTA E RANKING
# ==============================

def analisar_mercado():

    resultados = []

    for acao in acoes:

        r = analisar_acao(acao)

        if r:
            resultados.append(r)

    if not resultados:
        return "Erro na análise"

    df = pd.DataFrame(resultados)

    df_rank = df.sort_values("score",ascending=False).head(10)

    msg = "📊 RANKING OPORTUNIDADES B3\n\n"

    for i,row in df_rank.iterrows():

        msg += (
        f"{row['acao']} | "
        f"queda {round(row['queda']*100,2)}% | "
        f"prob alta {round(row['prob']*100,1)}%\n"
        )

    msg += "\n📋 TODAS AÇÕES ANALISADAS\n\n"

    for i,row in df.iterrows():

        msg += (
        f"{row['acao']} "
        f"queda:{round(row['queda']*100,2)}% "
        f"prob:{round(row['prob']*100,1)}%\n"
        )

    return msg


# ==============================
# NOTÍCIAS EM PORTUGUÊS
# ==============================

def noticias():

    feeds = [
    "https://www.infomoney.com.br/feed/",
    "https://www.valor.com.br/financas/rss",
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

    msg = "📰 PRINCIPAIS NOTÍCIAS DO MERCADO\n\n"

    for n in lista[:6]:

        msg += f"- {n}\n"

    return msg


# ==============================
# RELATÓRIO FINAL
# ==============================

def relatorio():

    mercado = analisar_mercado()

    news = noticias()

    return mercado + "\n\n" + news


# ==============================
# LOOP DO ROBÔ
# ==============================

print("robô quantitativo iniciado")

while True:

    try:

        mensagem = relatorio()

        print(mensagem)

        enviar(mensagem)

    except Exception as e:

        print("erro:",e)

    time.sleep(7200)
