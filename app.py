import time
import requests
import yfinance as yf
import pandas as pd
import feedparser

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","ABEV3.SA",
"BBAS3.SA","WEGE3.SA","B3SA3.SA","JBSS3.SA","RENT3.SA",
"LREN3.SA","PRIO3.SA","SUZB3.SA","RADL3.SA","RAIL3.SA"
]


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
# ANALISE HISTÓRICA
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

        retorno = close.pct_change()

        variacao_hoje = retorno.iloc[-1]

        preco = close.iloc[-1]

        historico = retorno.dropna()

        semelhantes = historico[
            (historico < variacao_hoje*1.2) &
            (historico > variacao_hoje*0.8)
        ]

        if len(semelhantes) < 6:
            return None

        subidas = 0

        for i in semelhantes.index:

            pos = dados.index.get_loc(i)

            if pos+1 < len(close):

                if close.iloc[pos+1] > close.iloc[pos]:

                    subidas += 1

        prob = subidas/len(semelhantes)

        if prob < 0.60:
            return None

        entrada = preco

        alvo_day = preco * 1.015

        alvo_swing = preco * 1.03

        return {
            "acao": ticker.replace(".SA",""),
            "preco": preco,
            "queda": variacao_hoje,
            "prob": prob,
            "entrada": entrada,
            "alvo_day": alvo_day,
            "alvo_swing": alvo_swing
        }

    except:

        return None


# =========================
# LISTA ORGANIZADA
# =========================

def oportunidades():

    lista = []

    for acao in acoes:

        r = analisar_acao(acao)

        if r:
            lista.append(r)

    if not lista:

        return "Nenhuma oportunidade encontrada hoje."

    df = pd.DataFrame(lista)

    df = df.sort_values("prob",ascending=False)

    msg = "📊 OPORTUNIDADES ESTATÍSTICAS B3\n\n"

    for i,row in df.iterrows():

        msg += (
        f"🟢 {row['acao']}\n"
        f"Preço atual: {round(row['preco'],2)}\n"
        f"Queda hoje: {round(row['queda']*100,2)}%\n"
        f"Prob. reversão: {round(row['prob']*100,1)}%\n"
        f"Entrada: {round(row['entrada'],2)}\n"
        f"Alvo DayTrade: {round(row['alvo_day'],2)}\n"
        f"Alvo Swing: {round(row['alvo_swing'],2)}\n\n"
        )

    return msg


# =========================
# MERCADO GLOBAL
# =========================

def mercado_global():

    sp = yf.download("^GSPC",period="5d",interval="1d",progress=False)
    oil = yf.download("BZ=F",period="5d",interval="1d",progress=False)
    usd = yf.download("USDBRL=X",period="5d",interval="1d",progress=False)

    sp_var = sp["Close"].pct_change().iloc[-1]
    oil_var = oil["Close"].pct_change().iloc[-1]
    usd_var = usd["Close"].pct_change().iloc[-1]

    msg = "🌎 MERCADO GLOBAL\n\n"

    msg += f"S&P500: {round(sp_var*100,2)}%\n"
    msg += f"Petróleo: {round(oil_var*100,2)}%\n"
    msg += f"Dólar: {round(usd_var*100,2)}%\n"

    if sp_var < -0.02:

        msg += "\n🚨 ALERTA DE ESTRESSE NO MERCADO\n"

    return msg


# =========================
# NOTÍCIAS
# =========================

def noticias():

    feed = "https://www.infomoney.com.br/feed/"

    data = feedparser.parse(feed)

    msg = "\n📰 NOTÍCIAS DO MERCADO\n\n"

    for item in data.entries[:5]:

        msg += f"- {item.title}\n"

    return msg


# =========================
# RELATORIO FINAL
# =========================

def relatorio():

    return (
        mercado_global() +
        "\n\n" +
        oportunidades() +
        noticias()
    )


print("robô iniciado")

while True:

    try:

        mensagem = relatorio()

        print(mensagem)

        enviar(mensagem)

    except Exception as e:

        print("erro:",e)

    time.sleep(3600)
