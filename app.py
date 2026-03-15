from src.scanner import analisar
from src.telegram_alerta import enviar
from src.acoes_b3 import acoes

import time
import datetime

def mercado_aberto():

    agora = datetime.datetime.now()

    return agora.hour >= 10 and agora.hour <= 17


while True:

    if mercado_aberto():

        oportunidades=[]

        for acao in acoes[:400]:

            try:

                r = analisar(acao)

                if r and r["queda"] < -2:

                    oportunidades.append(r)

            except:
                pass

        oportunidades = sorted(
            oportunidades,
            key=lambda x: x["queda"]
        )

        if oportunidades:

            msg = "🚨 OPORTUNIDADES B3\n\n"

            for o in oportunidades[:10]:

                msg += f"""
{o['ticker']}
Preço {o['preco']}
Queda {o['queda']}%
"""

            enviar(msg)

    time.sleep(300)
