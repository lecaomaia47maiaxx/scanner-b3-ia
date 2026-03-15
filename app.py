import requests
import time
import feedparser

TOKEN="8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID="8352381582"
API_KEY="59c25209cf3141f088781b53e576eb55"


def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url,data={"chat_id":CHAT_ID,"text":msg})
    except:
        print("Erro Telegram")


def preco(ticker):

    try:

        url=f"https://api.twelvedata.com/price?symbol={ticker}&apikey={API_KEY}"

        r=requests.get(url,timeout=10).json()

        if "price" in r:

            preco=float(r["price"])

            return preco

        else:

            return None

    except:

        return None


acoes=[
"PETR4:BVMF",
"VALE3:BVMF",
"ITUB4:BVMF",
"BBDC4:BVMF",
"BBAS3:BVMF",
"B3SA3:BVMF",
"WEGE3:BVMF",
"RENT3:BVMF",
"PRIO3:BVMF",
"LREN3:BVMF"
]


def scanner():

    sinais=[]

    for acao in acoes:

        p=preco(acao)

        if p:

            sinais.append({
                "acao":acao.replace(":BVMF",""),
                "preco":round(p,2)
            })

        time.sleep(8)

    return sinais


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


enviar("🤖 Robô iniciado no Railway")


while True:

    try:

        msg="🌎 RELATÓRIO FINANCEIRO\n\n"

        msg+="📰 Notícias\n"
        msg+=noticias()+"\n"

        dados=scanner()

        if dados:

            msg+="\n📈 Ações B3\n"

            for d in dados:

                msg+=f"{d['acao']} | R${d['preco']}\n"

        else:

            msg+="Sem dados de mercado agora"

        enviar(msg)

        print("Relatório enviado")

    except Exception as e:

        print(e)

    time.sleep(900)
