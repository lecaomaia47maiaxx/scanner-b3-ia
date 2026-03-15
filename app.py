import yfinance as yf
import time
import requests

TOKEN = "8675758808:AAEhsr9A0HwFazy92GFUndyh2oSJFEhlMEE"
CHAT_ID = "8675758808"

def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        print("Erro ao enviar telegram")

print("ROBÔ GLOBAL INICIADO")

# mensagem inicial
enviar("🤖 Robô iniciado com sucesso")

acoes = [
"PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
"WEGE3.SA","RENT3.SA","LREN3.SA","SUZB3.SA","PRIO3.SA",
"RADL3.SA","RAIL3.SA","B3SA3.SA","GGBR4.SA","USIM5.SA",
"CSNA3.SA","MGLU3.SA","CMIG4.SA","EQTL3.SA","SBSP3.SA",
"VBBR3.SA","UGPA3.SA","HAPV3.SA","TIMS3.SA"
]

indices
