import yfinance as yf
import pandas as pd
import numpy as np
import time
from telegram import Bot
from sklearn.ensemble import RandomForestClassifier

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

# lista ampla de ações líquidas
acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA",
"JBSS3.SA","RAIL3.SA","RADL3.SA","ELET3.SA","ELET6.SA",
"GGBR4.SA","USIM5.SA","CSNA3.SA","BRFS3.SA","HAPV3.SA",
"AZUL4.SA","GOLL4.SA","MGLU3.SA","NTCO3.SA","B3SA3.SA"
]

def baixar_dados(ticker):

    df = yf.download(ticker, period="2y", interval="1d")

    df["retorno"] = df["Close"].pct_change()
    df["ma20"] = df["Close"].rolling(20).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (100/(1+rs))

    df["volume_media"] = df["Volume"].rolling(20).mean()

    df["reversao"] = np.where(df["Close"].shift(-1) > df["Close"],1,0)

    return df.dropna()

def treinar_modelo(df):

    X = df[["retorno","rsi","Volume","volume_media"]]

    y = df["reversao"]

    model = RandomForestClassifier()

    model.fit(X,y)

    return model

def analisar_acao(ticker):

    df = baixar_dados(ticker)

    model = treinar_modelo(df)

    ultimo = df.iloc[-1]

    queda = ultimo["retorno"]*100

    if queda > -1:
        return None

    X_pred = [[
        ultimo["retorno"],
        ultimo["rsi"],
        ultimo["Volume"],
        ultimo["volume_media"]
    ]]

    prob = model.predict_proba(X_pred)[0][1]

    if prob < 0.60:
        return None

    preco = ultimo["Close"]

    alvo_day = preco*1.02
    alvo_swing = preco*1.05
    stop = preco*0.98

    volume_inst = ultimo["Volume"] > ultimo["volume_media"]*1.5

    return {
        "acao":ticker.replace(".SA",""),
        "preco":round(preco,2),
        "queda":round(queda,2),
        "prob":round(prob*100,1),
        "entrada":round(preco,2),
        "alvo_day":round(alvo_day,2),
        "alvo_swing":round(alvo_swing,2),
        "stop":round(stop,2),
        "volume":volume_inst
    }

def escanear_mercado():

    oportunidades=[]

    for acao in acoes:

        try:

            r = analisar_acao(acao)

            if r:
                oportunidades.append(r)

        except:
            pass

    oportunidades=sorted(
        oportunidades,
        key=lambda x:x["prob"],
        reverse=True
    )

    return oportunidades[:20]

def gerar_mensagem(lista):

    msg="📊 TOP OPORTUNIDADES B3\n\n"

    for a in lista:

        msg+=f"""
📈 {a['acao']}

Preço atual: {a['preco']}
Queda: {a['queda']}%

Entrada: {a['entrada']}

🎯 Day Trade: {a['alvo_day']}
📊 Swing: {a['alvo_swing']}
⛔ Stop: {a['stop']}

Probabilidade: {a['prob']}%

"""

        if a["volume"]:
            msg+="💰 Volume institucional detectado\n"

        msg+="-----------------\n"

    return msg

def loop():

    while True:

        lista=escanear_mercado()

        if lista:

            texto=gerar_mensagem(lista)

            bot.send_message(
                chat_id=CHAT_ID,
                text=texto
            )

        time.sleep(1800)

if __name__=="__main__":
    loop()
