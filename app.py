import yfinance as yf
import pandas as pd
import requests
import time
import feedparser

TOKEN="8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID="8352381582"

acoes=[
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","PRIO3.SA","B3SA3.SA","JBSS3.SA","RENT3.SA",
"LREN3.SA","SUZB3.SA"
]

# =================================
# TELEGRAM
# =================================

def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload={
        "chat_id":CHAT_ID,
        "text":msg
    }

    requests.post(url,data=payload)


# =================================
# CALCULO ENTRADA POR VARIAÇÃO
# =================================

def calcular_entrada(preco,var):

    try:

        entrada=preco/(1+var)

        return entrada

    except:

        return preco


# =================================
# ANALISE ESTATISTICA
# =================================

def analisar_acao(ticker):

    try:

        dados=yf.download(ticker,period="5y",interval="1d",progress=False)

        if dados.empty:
            return None

        close=dados["Close"]

        preco=float(close.iloc[-1])

        var=float(close.pct_change().iloc[-1])

        if var>-0.02:
            return None

        entrada=calcular_entrada(preco,var)

        alvo=preco*1.02

        return{
        "acao":ticker.replace(".SA",""),
        "preco":preco,
        "queda":var,
        "entrada":entrada,
        "alvo":alvo
        }

    except Exception as e:

        print("erro analise",ticker,e)

        return None


# =================================
# LISTA OPORTUNIDADES
# =================================

def oportunidades():

    lista=[]

    for acao in acoes:

        r=analisar_acao(acao)

        if r:
            lista.append(r)

    if not lista:
        return "📊 Nenhuma oportunidade encontrada."

    df=pd.DataFrame(lista)

    df=df.sort_values("queda")

    msg="📊 OPORTUNIDADES B3\n\n"

    for _,row in df.iterrows():

        msg+=(
        f"🟢 {row['acao']}\n"
        f"Preço atual: {round(row['preco'],2)}\n"
        f"Queda do dia: {round(row['queda']*100,2)}%\n"
        f"Entrada: {round(row['entrada'],2)}\n"
        f"Alvo: {round(row['alvo'],2)}\n\n"
        )

    return msg


# =================================
# SWING TRADE EMA
# =================================

def swing_trade(ticker):

    try:

        d=yf.download(ticker,period="1y",interval="1d",progress=False)
        w=yf.download(ticker,period="5y",interval="1wk",progress=False)
        m=yf.download(ticker,period="60d",interval="60m",progress=False)

        if d.empty or w.empty or m.empty:
            return None

        close_d=d["Close"]
        close_w=w["Close"]
        close_m=m["Close"]

        preco=float(close_d.iloc[-1])

        ema17=close_d.ewm(span=17).mean().iloc[-1]
        ema72=close_d.ewm(span=72).mean().iloc[-1]

        distancia=min(
        abs(preco-ema17)/preco,
        abs(preco-ema72)/preco
        )

        if distancia>0.01:
            return None

        ema72_w=close_w.ewm(span=72).mean().iloc[-1]
        preco_w=float(close_w.iloc[-1])

        compra=preco_w>ema72_w
        venda=preco_w<ema72_w

        topo=max(close_m.iloc[-20:])
        fundo=min(close_m.iloc[-20:])

        preco_m=float(close_m.iloc[-1])

        if compra and preco_m>topo:

            return f"🟢 SWING COMPRA {ticker.replace('.SA','')} rompendo topo"

        if venda and preco_m<fundo:

            return f"🔴 SWING VENDA {ticker.replace('.SA','')} rompendo fundo"

        return None

    except:

        return None


# =================================
# SCANNER SWING
# =================================

def scanner_swing():

    sinais=[]

    for acao in acoes:

        r=swing_trade(acao)

        if r:
            sinais.append(r)

    if not sinais:
        return "📊 Nenhum setup swing encontrado."

    msg="\n📊 SETUPS SWING TRADE\n\n"

    for s in sinais:

        msg+=s+"\n"

    return msg


# =================================
# MERCADO GLOBAL
# =================================

def mercado_global():

    try:

        sp=yf.download("^GSPC",period="5d",interval="1d",progress=False)
        oil=yf.download("BZ=F",period="5d",interval="1d",progress=False)
        usd=yf.download("USDBRL=X",period="5d",interval="1d",progress=False)

        sp_var=float(sp["Close"].pct_change().iloc[-1])
        oil_var=float(oil["Close"].pct_change().iloc[-1])
        usd_var=float(usd["Close"].pct_change().iloc[-1])

        msg="🌎 MERCADO GLOBAL\n\n"

        msg+=f"S&P500: {round(sp_var*100,2)}%\n"
        msg+=f"Petróleo: {round(oil_var*100,2)}%\n"
        msg+=f"Dólar: {round(usd_var*100,2)}%\n"

        if sp_var<-0.02:

            msg+="\n🚨 MERCADO EM PÂNICO\n"

        return msg

    except:

        return ""


# =================================
# NOTICIAS EM PORTUGUES
# =================================

def noticias():

    try:

        feed="https://www.infomoney.com.br/feed/"

        data=feedparser.parse(feed)

        msg="📰 NOTÍCIAS MERCADO\n\n"

        for item in data.entries[:5]:

            msg+=f"- {item.title}\n"

        return msg

    except:

        return ""


# =================================
# LOOP PRINCIPAL
# =================================

print("robô iniciado")

ultimo_noticia=0
ultimo_scanner=0

while True:

    agora=time.time()

    try:

        if agora-ultimo_noticia>900:

            enviar(noticias())

            ultimo_noticia=agora

        if agora-ultimo_scanner>3600:

            enviar(mercado_global())
            enviar(oportunidades())
            enviar(scanner_swing())

            ultimo_scanner=agora

    except Exception as e:

        print("erro",e)

    time.sleep(60)
