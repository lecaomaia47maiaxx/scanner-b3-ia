import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser

# ==============================
# CONFIG TELEGRAM
# ==============================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# ==============================
# AÇÕES MAIS LÍQUIDAS B3
# ==============================

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","ABEV3.SA",
"BBAS3.SA","WEGE3.SA","B3SA3.SA","JBSS3.SA","RENT3.SA",
"LREN3.SA","PRIO3.SA","SUZB3.SA","RADL3.SA","RAIL3.SA",
"GGBR4.SA","USIM5.SA","CSNA3.SA","EQTL3.SA","ENBR3.SA"
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
# ANÁLISE ESTATÍSTICA
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

        retorno = close.pct_change(5)

        queda_atual = retorno.iloc[-1]

        if queda_atual > -0.03:
            return None

        historico = retorno.dropna()

        semelhantes = historico[
            (historico < queda_atual * 1.2) &
            (historico > queda_atual * 0.8)
        ]

        if len(semelhantes) < 6:
            return None

        subidas = 0

        for i in semelhantes.index:

            pos = dados.index.get_loc(i)

            if pos + 5 < len(close):

                preco_futuro = close.iloc[pos+5]
                preco_atual = close.iloc[pos]

                if preco_futuro > preco_atual:
                    subidas += 1

        probabilidade = subidas / len(semelhantes)

        retorno_medio = close.pct_change(5).mean()

        score = probabilidade * abs(queda_atual)

        return {
            "acao": ticker.replace(".SA",""),
            "queda": queda_atual,
            "prob": probabilidade,
            "ocorrencias": len(semelhantes),
            "score": score
        }

    except:

        return None


# ==============================
# GERAR RANKING
# ==============================

def ranking_oportunidades():

    resultados = []

    for acao in acoes:

        analise = analisar_acao(acao)

        if analise:
            resultados.append(analise)

    if not resultados:
        return "Nenhuma oportunidade estatística encontrada."

    df = pd.DataFrame(resultados)

    df = df.sort_values("score",ascending=False)

    top10 = df.head(10)

    msg = "📊 TOP 10 OPORTUNIDADES ESTATÍSTICAS B3\n\n"

    for i,row in top10.iterrows():

        msg += (
            f"{row['acao']}\n"
            f"queda recente: {round(row['queda']*100,2)}%\n"
            f"probabilidade alta: {round(row['prob']*100,1)}%\n"
            f"ocorrências históricas: {row['ocorrencias']}\n\n"
        )

    return msg


# ==============================
# NOTÍCIAS DO MERCADO GLOBAL
# ==============================

def noticias_mercado():

    feeds = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.investing.com/rss/news_25.rss"
    ]

    noticias = []

    for feed in feeds:

        try:

            data = feedparser.parse(feed)

            for item in data.entries[:2]:

                noticias.append(item.title)

        except:
            pass

    msg = "🌎 PRINCIPAIS NOTÍCIAS DO MERCADO GLOBAL\n\n"

    for n in noticias[:6]:

        msg += f"- {n}\n"

    return msg


# ==============================
# RELATÓRIO COMPLETO
# ==============================

def relatorio():

    ranking = ranking_oportunidades()

    news = noticias_mercado()

    msg = ranking + "\n\n" + news

    return msg


# ==============================
# LOOP DO ROBÔ
# ==============================

print("Robô quantitativo iniciado")

while True:

    try:

        mensagem = relatorio()

        print(mensagem)

        enviar(mensagem)

    except Exception as e:

        print("erro:",e)

    # roda a cada 2 horas
    time.sleep(7200)
