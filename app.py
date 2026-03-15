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
        print("erro telegram")


# pegar preço no yahoo
def preco_ativo(ticker):

    try:

        url=f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

        r=requests.get(url,timeout=10).json()

        dados=r["chart"]["result"][0]["meta"]

        preco=dados["regularMarketPrice"]

        anterior=dados["previousClose"]

        variacao=(preco-anterior)/anterior*100

        return preco,variacao

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


# ações mais líquidas da B3
acoes=[
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"B3SA3.SA","WEGE3.SA","RENT3.SA","PRIO3.SA","LREN3.SA",
"RADL3.SA","RAIL3.SA","SUZB3.SA","GGBR4.SA","USIM5.SA",
"CSNA3.SA","ELET3.SA","MGLU3.SA","HAPV3.SA","EQTL3.SA",
"SBSP3.SA","VBBR3.SA","UGPA3.SA","TIMS3.SA","BRAP4.SA"
]


# scanner ações
def scanner():

    sinais=[]

    for acao in acoes:

        preco,var=preco_ativo(acao)

        if preco:

            score=abs(var)*10

            sinais.append({
            "acao":acao.replace(".SA",""),
            "preco":round(preco,2),
            "score":round(score,1)
            })

        time.sleep(1)

    sinais=sorted(sinais,key=lambda x:x["score"],reverse=True)

    return sinais[:10]


# notícias
def noticias():

    feed=feedparser.parse("https://news.google.com/rss/search?q=mercado+financeiro")

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
