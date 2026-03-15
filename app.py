import requests
import time
import feedparser

TOKEN="8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID="8352381582"

print("ROBÔ GLOBAL INICIADO")


def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url,data={"chat_id":CHAT_ID,"text":msg})
    except:
        print("Erro Telegram")


# pegar preço via BRAPI
def preco_ativo(ticker):

    try:

        url=f"https://brapi.dev/api/quote/{ticker}"

        r=requests.get(url).json()

        dados=r["results"][0]

        preco=dados["regularMarketPrice"]

        var=dados["regularMarketChangePercent"]

        return preco,var

    except:

        return None,None


# índices globais
indices={
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOW":"^DJI"
}


def analisar_indices():

    texto=""

    for nome,ticker in indices.items():

        preco,var=preco_ativo(ticker)

        if preco:

            texto+=f"{nome}: {round(var,2)}%\n"

    if texto=="":
        texto="Sem dados\n"

    return texto


# bitcoin
def analisar_bitcoin():

    preco,var=preco_ativo("BTC-USD")

    if preco:

        return f"Bitcoin ${round(preco,2)} ({round(var,2)}%)"

    return "Bitcoin sem dados"


# ações líquidas B3
acoes=[
"PETR4","VALE3","ITUB4","BBDC4","BBAS3",
"B3SA3","WEGE3","RENT3","PRIO3","LREN3",
"RADL3","RAIL3","SUZB3","GGBR4","USIM5",
"CSNA3","ELET3","MGLU3","HAPV3","EQTL3"
]


def scanner():

    sinais=[]

    for acao in acoes:

        preco,var=preco_ativo(acao)

        if preco:

            score=abs(var)*10

            sinais.append({
                "acao":acao,
                "preco":round(preco,2),
                "score":round(score,1)
            })

        time.sleep(1)

    sinais=sorted(sinais,key=lambda x:x["score"],reverse=True)

    return sinais[:10]


# notícias
def noticias():

    feed=feedparser.parse(
    "https://news.google.com/rss/search?q=mercado+financeiro+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    )

    texto=""

    for i in range(5):

        try:
            texto+=feed.entries[i].title+"\n"
        except:
            pass

    return texto


enviar("🤖 Robô financeiro iniciado")


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
