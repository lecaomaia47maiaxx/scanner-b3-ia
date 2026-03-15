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


# pegar vários ativos ao mesmo tempo
def pegar_ativos(lista):

    try:

        ativos=",".join(lista)

        url=f"https://brapi.dev/api/quote/{ativos}"

        r=requests.get(url,timeout=10).json()

        dados={}

        for item in r["results"]:

            dados[item["symbol"]] = {
                "preco": item.get("regularMarketPrice"),
                "var": item.get("regularMarketChangePercent")
            }

        return dados

    except:

        return {}


# índices globais
indices={
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOW":"^DJI"
}


# ações líquidas B3
acoes=[
"PETR4","VALE3","ITUB4","BBDC4","BBAS3",
"B3SA3","WEGE3","RENT3","PRIO3","LREN3",
"RADL3","RAIL3","SUZB3","GGBR4","USIM5",
"CSNA3","ELET3","MGLU3","HAPV3","EQTL3"
]


def analisar_indices(dados):

    texto=""

    for nome,ticker in indices.items():

        if ticker in dados:

            var=dados[ticker]["var"]

            if var!=None:

                texto+=f"{nome}: {round(var,2)}%\n"

    if texto=="":
        texto="Sem dados\n"

    return texto


def analisar_bitcoin(dados):

    if "BTC-USD" in dados:

        preco=dados["BTC-USD"]["preco"]
        var=dados["BTC-USD"]["var"]

        if preco:

            return f"Bitcoin ${round(preco,2)} ({round(var,2)}%)"

    return "Bitcoin sem dados"


def scanner(dados):

    sinais=[]

    for acao in acoes:

        if acao in dados:

            preco=dados[acao]["preco"]
            var=dados[acao]["var"]

            if preco and var!=None:

                score=abs(var)*10

                sinais.append({
                    "acao":acao,
                    "preco":round(preco,2),
                    "score":round(score,1)
                })

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


enviar("🤖 Robô financeiro iniciado com sucesso")


while True:

    try:

        print("Gerando relatório...")

        ativos=list(indices.values()) + acoes + ["BTC-USD"]

        dados=pegar_ativos(ativos)

        msg="🌎 RELATÓRIO GLOBAL\n\n"

        msg+="📊 ÍNDICES GLOBAIS\n"
        msg+=analisar_indices(dados)+"\n"

        msg+="₿ "+analisar_bitcoin(dados)+"\n\n"

        msg+="📰 Notícias\n"
        msg+=noticias()+"\n"

        sinais=scanner(dados)

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
