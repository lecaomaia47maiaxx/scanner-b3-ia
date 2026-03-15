import yfinance as yf
import pandas as pd
import requests
import feedparser
import time

TOKEN="8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID= "8352381582"

print("ROBÔ GLOBAL INICIADO")

# enviar mensagem telegram
def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url,data={"chat_id":CHAT_ID,"text":msg})
    except:
        print("erro telegram")


# download seguro de dados
def baixar_dados(ticker,periodo="5d",intervalo=None):

    try:

        df=yf.download(
        ticker,
        period=periodo,
        interval=intervalo,
        progress=False,
        threads=False)

        time.sleep(1)

        if df is None or df.empty:
            return None

        return df

    except:
        return None


# índices globais
indices={
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOW":"^DJI"
}

bitcoin="BTC-USD"

# lista base B3
base_acoes=[
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","RENT3.SA","LREN3.SA","PRIO3.SA","RADL3.SA",
"RAIL3.SA","B3SA3.SA","GGBR4.SA","USIM5.SA","CSNA3.SA",
"MGLU3.SA","CMIG4.SA","EQTL3.SA","SBSP3.SA","VBBR3.SA",
"UGPA3.SA","HAPV3.SA","TIMS3.SA","BRAP4.SA","KLBN11.SA",
"SUZB3.SA","CPFE3.SA","CPLE6.SA","TAEE11.SA","ELET3.SA"
]

# expandir para ~300
acoes=base_acoes*10


# análise índices globais
def analisar_indices():

    texto=""

    for nome,ticker in indices.items():

        df=baixar_dados(ticker,"5d")

        if df is None:
            continue

        try:

            close=df["Close"].dropna()

            if len(close)<2:
                continue

            atual=float(close.iloc[-1])
            anterior=float(close.iloc[-2])

            var=(atual-anterior)/anterior*100

            texto+=f"{nome}: {round(var,2)}%\n"

        except:
            continue

    if texto=="":
        texto="Sem dados\n"

    return texto


# bitcoin
def analisar_bitcoin():

    df=baixar_dados(bitcoin,"5d")

    if df is None:
        return "Bitcoin sem dados"

    try:

        close=df["Close"].dropna()

        atual=float(close.iloc[-1])
        anterior=float(close.iloc[-2])

        var=(atual-anterior)/anterior*100

        return f"Bitcoin ${round(atual,2)} ({round(var,2)}%)"

    except:
        return "Bitcoin sem dados"


# detectar acumulação institucional
def detectar_acumulacao(df):

    try:

        vol=df["Volume"]

        if len(vol)<20:
            return False

        media=vol.rolling(20).mean()

        atual=float(vol.iloc[-1])
        media=float(media.iloc[-1])

        if atual>media*1.8:
            return True

        return False

    except:
        return False


# analisar ação
def analisar_acao(ticker):

    df=baixar_dados(ticker,"5d","5m")

    if df is None:
        return None

    try:

        close=df["Close"].dropna()

        if len(close)<2:
            return None

        atual=float(close.iloc[-1])
        anterior=float(close.iloc[-2])

        variacao=(atual-anterior)/anterior*100

        acumulacao=detectar_acumulacao(df)

        score=abs(variacao)*10

        if acumulacao:
            score+=30

        return{
        "acao":ticker.replace(".SA",""),
        "preco":round(atual,2),
        "score":round(score,1)
        }

    except:

        return None


# scanner mercado B3
def scanner():

    sinais=[]

    for acao in acoes:

        r=analisar_acao(acao)

        if r:
            sinais.append(r)

        time.sleep(0.5)

    sinais=sorted(sinais,key=lambda x:x["score"],reverse=True)

    return sinais[:10]


# notícias financeiras
def noticias():

    feed=feedparser.parse("https://news.google.com/rss/search?q=mercado+financeiro")

    texto=""

    for i in range(5):

        try:
            texto+=feed.entries[i].title+"\n"
        except:
            pass

    return texto


# loop principal
enviar("🤖 Robô financeiro iniciado com sucesso")

while True:

    try:

        print("Gerando relatório...")

        msg="🌎 RELATÓRIO GLOBAL\n\n"

        msg+="📊 ÍNDICES GLOBAIS\n"
        msg+=analisar_indices()+"\n"

        msg+="₿ "+analisar_bitcoin()+"\n\n"

        msg+="📰 Notícias\n"
        msg+=noticias()+"\n"

        sinais=scanner()

        if sinais:

            msg+="\n📈 Ranking B3\n"

            for s in sinais:

                msg+=f"{s['acao']} | R${s['preco']} | score {s['score']}\n"

        else:

            msg+="Sem oportunidades na B3 agora"

        enviar(msg)

        print("Relatório enviado")

    except Exception as e:

        print("Erro:",e)

    time.sleep(600)
