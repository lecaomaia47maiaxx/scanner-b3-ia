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
    except Exception as e:
        print("erro telegram:",e)


# ==============================
# ANALISE ESTATISTICA
# ==============================

def analisar_acao(ticker):

    try:

        dados = yf.download(
            ticker,
            period="10y",
            interval="1d",
            progress=False
        )

        if dados.empty:
            return None

        close = dados["Close"].squeeze()

        retorno = close.pct_change()

        variacao_hoje = float(retorno.iloc[-1])

        preco = float(close.iloc[-1])

        historico = retorno.dropna()

        semelhantes = historico[
            (historico < variacao_hoje * 1.2) &
            (historico > variacao_hoje * 0.8)
        ]

        if len(semelhantes) < 6:
            return None

        subidas = 0

        for data in semelhantes.index:

            pos = dados.index.get_loc(data)

            if pos + 1 < len(close):

                preco_futuro = float(close.iloc[pos+1])
                preco_base = float(close.iloc[pos])

                if preco_futuro > preco_base:

                    subidas += 1

        prob = subidas / len(semelhantes)

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

    except Exception as e:

        print("erro análise:",ticker,e)

        return None


# ==============================
# LISTA DE OPORTUNIDADES
# ==============================

def oportunidades():

    resultados = []

    for acao in acoes:

        r = analisar_acao(acao)

        if r is not None:
            resultados.append(r)

    if len(resultados) == 0:

        return "📊 Nenhuma oportunidade encontrada hoje."

    df = pd.DataFrame(resultados)

    df = df.sort_values("prob",ascending=False)

    msg = "📊 OPORTUNIDADES ESTATÍSTICAS B3\n\n"

    for _,row in df.iterrows():

        msg += (
        f"🟢 {row['acao']}\n"
        f"Preço atual: {round(row['preco'],2)}\n"
        f"Queda hoje: {round(row['queda']*100,2)}%\n"
        f"Probabilidade histórica: {round(row['prob']*100,1)}%\n"
        f"Entrada sugerida: {round(row['entrada'],2)}\n"
        f"Alvo DayTrade: {round(row['alvo_day'],2)}\n"
        f"Alvo Swing: {round(row['alvo_swing'],2)}\n\n"
        )

    return msg


# ==============================
# MERCADO GLOBAL
# ==============================

def mercado_global():

    try:

        sp = yf.download("^GSPC",period="5d",interval="1d",progress=False)
        oil = yf.download("BZ=F",period="5d",interval="1d",progress=False)
        usd = yf.download("USDBRL=X",period="5d",interval="1d",progress=False)

        sp_var = float(sp["Close"].pct_change().iloc[-1])
        oil_var = float(oil["Close"].pct_change().iloc[-1])
        usd_var = float(usd["Close"].pct_change().iloc[-1])

        msg = "🌎 MERCADO GLOBAL\n\n"

        msg += f"S&P500: {round(sp_var*100,2)}%\n"
        msg += f"Petróleo: {round(oil_var*100,2)}%\n"
        msg += f"Dólar: {round(usd_var*100,2)}%\n"

        if sp_var < -0.02:

            msg += "\n🚨 ALERTA DE ESTRESSE NO MERCADO\n"

        return msg

    except Exception as e:

        print("erro mercado global:",e)

        return ""


# ==============================
# NOTICIAS
# ==============================

def noticias():

    try:

        feed = "https://www.infomoney.com.br/feed/"

        data = feedparser.parse(feed)

        msg = "\n📰 NOTÍCIAS DO MERCADO\n\n"

        for item in data.entries[:5]:

            msg += f"- {item.title}\n"

        return msg

    except:

        return ""


# ==============================
# RELATORIO FINAL
# ==============================

def relatorio():

    return mercado_global() + "\n\n" + oportunidades() + noticias()


print("robô iniciado")

while True:

    try:

        mensagem = relatorio()

        print(mensagem)

        enviar(mensagem)

    except Exception as e:

        print("erro geral:",e)

    time.sleep(3600)
