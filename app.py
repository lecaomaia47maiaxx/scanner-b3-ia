import requests
import time
import feedparser

TOKEN="8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID="8352381582"
API_KEY="OYSICYD1972XILCB"

print("ROBÔ GLOBAL INICIADO")


def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url,data={"chat_id":CHAT_ID,"text":msg})
    except:
        print("Erro Telegram")


# pegar preço de ativo
def preco_acao(ticker):

    try:

        url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}"

        r=requests.get(url).json()

        dados=r["Global Quote"]

        preco=float(dados["05. price"])
        var=float(dados["10. change percent"].replace("%",""))

        return preco,var

    except:

        return None,None


# ações líquidas B3
acoes=[
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"B3SA3.SA","WEGE3.SA","RENT3.SA","PRIO3.SA","LREN3.SA"
]


def scanner():

    sinais=[]

    for acao in acoes:

        preco,var=preco_acao(acao)

        if preco:

            score=abs(var)*10

            sinais.append({
                "acao":acao.replace(".SA",""),
                "preco":round(preco,2),
                "score":round(score,1)
            })

        time.sleep(15)  # limite da API

    sinais=sorted(sinais,key=lambda x:x["score"],reverse=True)

    return sinais[:5]


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

        msg="🌎 RELATÓRIO FINANCEIRO\n\n"

        msg+="📰 Notícias\n"
        msg+=noticias()+"\n"

        sinais=scanner()

        if sinais:

            msg+="\n📈 Ranking B3\n"

            for s in sinais:

                msg+=f"{s['acao']} | R${s['preco']} | score {s['score']}\n"

        else:

            msg+="Sem dados de mercado agora"

        enviar(msg)

        print("Relatório enviado")

    except Exception as e:

        print("Erro:",e)

    time.sleep(900)
