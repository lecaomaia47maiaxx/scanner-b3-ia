import yfinance as yf
import requests
import time

# ==============================
# CONFIG
# ==============================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"
GNEWS_API = "de1c856f0bb4160d37e29d7e20f06c54"

# ==============================
# AÇÕES MAIS LÍQUIDAS B3
# (JBSS3 REMOVIDA DEFINITIVAMENTE)
# ==============================

ATIVOS = [
    "PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA",
    "BBAS3.SA","WEGE3.SA","PRIO3.SA","RENT3.SA",
    "SUZB3.SA","ABEV3.SA"
]

# ==============================
# TELEGRAM
# ==============================

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

def enviar_imagem(url_img, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "photo": url_img,
        "caption": caption,
        "parse_mode": "Markdown"
    })

# ==============================
# AJUSTE DE COLUNA
# ==============================

def ajustar(col):
    if col is None:
        return None
    if hasattr(col, "columns"):
        col = col.iloc[:, 0]
    return col.squeeze()

# ==============================
# DADOS (COM PROTEÇÃO TOTAL)
# ==============================

def get_dados(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False, threads=False)
        if data is None or data.empty:
            return None
        return data
    except:
        return None

# ==============================
# ANÁLISE (REVERSÃO + PULLBACK)
# ==============================

def analisar_ativo(ticker):
    try:
        data = get_dados(ticker)
        if data is None or len(data) < 30:
            return None

        close = ajustar(data.get("Close"))
        volume = ajustar(data.get("Volume"))

        if close is None or volume is None:
            return None

        close = close.dropna()
        volume = volume.dropna()

        mm9 = close.rolling(9).mean()
        mm21 = close.rolling(21).mean()

        preco = float(close.iloc[-1])
        anterior = float(close.iloc[-2])
        variacao = ((preco - anterior) / anterior) * 100

        # REVERSÃO
        cruzamento = mm9.iloc[-2] < mm21.iloc[-2] and mm9.iloc[-1] > mm21.iloc[-1]

        # PULLBACK
        distancia_mm9 = ((preco - mm9.iloc[-1]) / mm9.iloc[-1]) * 100

        entrada = None
        sinal = "NEUTRO ⚪"

        if cruzamento:
            sinal = "REVERSÃO 🔄"

        if mm9.iloc[-1] > mm21.iloc[-1] and distancia_mm9 < 1:
            entrada = round(mm9.iloc[-1], 2)
            sinal = "COMPRA POR PULLBACK 🟢🔥"

        # VOLUME
        vol_atual = float(volume.iloc[-1])
        vol_media = float(volume.rolling(20).mean().iloc[-1])
        volume_status = "FORTE 🔥" if vol_atual > vol_media else "FRACO 💤"

        return {
            "ticker": ticker.replace(".SA",""),
            "preco": round(preco,2),
            "variacao": round(variacao,2),
            "entrada": entrada,
            "volume": volume_status,
            "sinal": sinal
        }

    except Exception as e:
        print("Erro na análise:", ticker)
        return None

# ==============================
# SCANNER
# ==============================

def scanner():
    resultados = []
    alertas = []

    for ativo in ATIVOS:
        r = analisar_ativo(ativo)

        if r is None:
            continue

        resultados.append(r)

        if "🔥" in r["sinal"]:
            alertas.append(r)

    return resultados, alertas

# ==============================
# NOTÍCIAS GNEWS
# ==============================

def buscar_noticias():
    url = f"https://gnews.io/api/v4/top-headlines?token={GNEWS_API}&lang=pt&topic=business"

    try:
        r = requests.get(url).json()
        return r.get("articles", [])[:5]
    except:
        return []

# ==============================
# RELATÓRIO
# ==============================

def enviar_relatorio():
    resultados, alertas = scanner()

    # ALERTAS
    if alertas:
        msg = "🚨 *ALERTAS DE ENTRADA*\n\n"
        for a in alertas:
            msg += (
                f"🔥 *{a['ticker']}*\n"
                f"💰 Preço: R$ {a['preco']}\n"
                f"🎯 Entrada: R$ {a['entrada']}\n"
                f"📊 Volume: {a['volume']}\n"
                f"⚡ {a['sinal']}\n\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
        enviar_telegram(msg)

    # COTAÇÕES
    cot = "💰 *COTAÇÕES DAS AÇÕES*\n\n"
    for r in resultados:
        emoji = "🟢" if r["variacao"] > 0 else "🔴"
        cot += f"{emoji} {r['ticker']} → R$ {r['preco']} ({r['variacao']}%)\n"

    enviar_telegram(cot)

    # NOTÍCIAS
    noticias = buscar_noticias()

    for n in noticias:
        titulo = n["title"]
        desc = n["description"] or ""
        link = n["url"]
        img = n.get("image")

        caption = f"📰 *{titulo}*\n\n{desc}\n\n🔗 {link}"

        if img:
            enviar_imagem(img, caption)
        else:
            enviar_telegram(caption)

# ==============================
# LOOP
# ==============================

while True:
    try:
        print("Rodando robô...")
        enviar_relatorio()
        print("Relatório enviado!")
    except Exception as e:
        print("Erro geral:", e)

    time.sleep(1800)
