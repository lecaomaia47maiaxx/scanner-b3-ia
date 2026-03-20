import yfinance as yf
import requests
import time

# ==============================
# CONFIG TELEGRAM
# ==============================

TOKEN = "8628983709:AAE5MH-87tpO0_JSiSlj-RgphyZpRgck3Oc"
CHAT_ID = "8352381582"

# ==============================
# ATIVOS (SEM JBSS3)
# ==============================

ATIVOS = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "ABEV3.SA",
    "WEGE3.SA",
    "BBAS3.SA",
    "RENT3.SA",
    "SUZB3.SA",
    "PRIO3.SA"
]

# ==============================
# TELEGRAM SEND
# ==============================

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# ==============================
# DADOS COM FALLBACK (ANTI ERRO)
# ==============================

def get_dados(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if data.empty:
            raise Exception("Erro period")

        return data

    except:
        try:
            data = yf.download(ticker, start="2023-01-01", interval="1d", progress=False)

            if data.empty:
                return None

            return data

        except:
            return None

# ==============================
# ANÁLISE INSTITUCIONAL
# ==============================

def analisar_ativo(ticker):
    data = get_dados(ticker)

    if data is None or len(data) < 50:
        return None

    close = data["Close"]
    volume = data["Volume"]

    mm9 = close.rolling(9).mean()
    mm21 = close.rolling(21).mean()

    # Tendência
    tendencia = "ALTA 📈" if mm9.iloc[-1] > mm21.iloc[-1] else "BAIXA 📉"

    # Volume
    vol_atual = volume.iloc[-1]
    vol_media = volume.rolling(20).mean().iloc[-1]

    volume_status = "FORTE 🔥" if vol_atual > vol_media else "FRACO 💤"

    # Fluxo
    variacao = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

    if variacao > 1:
        fluxo = "COMPRA 🟢"
    elif variacao < -1:
        fluxo = "VENDA 🔴"
    else:
        fluxo = "NEUTRO ⚪"

    return {
        "ticker": ticker.replace(".SA", ""),
        "preco": round(close.iloc[-1], 2),
        "tendencia": tendencia,
        "volume": volume_status,
        "fluxo": fluxo,
        "variacao": round(variacao, 2)
    }

# ==============================
# SCANNER B3
# ==============================

def scanner_b3():
    resultados = []

    for ativo in ATIVOS:
        analise = analisar_ativo(ativo)

        if analise:
            resultados.append(analise)

    oportunidades = [
        r for r in resultados
        if r["fluxo"] == "COMPRA 🟢" and r["volume"] == "FORTE 🔥"
    ]

    return resultados, oportunidades

# ==============================
# NOTÍCIAS (API GRATUITA)
# ==============================

def buscar_noticias():
    url = "https://newsapi.org/v2/top-headlines?category=business&language=pt&apiKey=SUA_API_AQUI"
    
    try:
        r = requests.get(url).json()
        artigos = r.get("articles", [])[:5]

        noticias = []
        for a in artigos:
            noticias.append({
                "titulo": a["title"],
                "resumo": a["description"] or "",
                "link": a["url"]
            })

        return noticias

    except:
        return []

# ==============================
# FORMATAR NOTÍCIAS
# ==============================

def formatar_noticias(noticias):
    texto = "📰 *NOTÍCIAS DO MERCADO*\n\n"

    for n in noticias:
        texto += f"🟡 *{n['titulo']}*\n"
        texto += f"{n['resumo']}\n"
        texto += f"🔗 {n['link']}\n\n"
        texto += "━━━━━━━━━━━━━━━\n\n"

    return texto

# ==============================
# FORMATAR ANÁLISE
# ==============================

def formatar_analises(resultados, oportunidades):
    texto = "📊 *SCANNER INSTITUCIONAL B3*\n\n"

    for r in resultados:
        texto += (
            f"🏢 *{r['ticker']}*\n"
            f"💰 Preço: R$ {r['preco']}\n"
            f"📈 Tendência: {r['tendencia']}\n"
            f"📊 Volume: {r['volume']}\n"
            f"⚡ Fluxo: {r['fluxo']}\n"
            f"📉 Variação: {r['variacao']}%\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
        )

    texto += "\n🚀 *OPORTUNIDADES DO DIA*\n\n"

    if oportunidades:
        for o in oportunidades:
            texto += (
                f"🟢 *{o['ticker']}* FORÇA COMPRADORA\n"
                f"💰 {o['preco']} | 📈 {o['variacao']}%\n\n"
            )
    else:
        texto += "⚠️ Nenhuma oportunidade forte no momento\n"

    return texto

# ==============================
# RELATÓRIO FINAL
# ==============================

def enviar_relatorio():
    noticias = buscar_noticias()
    texto_noticias = formatar_noticias(noticias)

    resultados, oportunidades = scanner_b3()
    texto_analise = formatar_analises(resultados, oportunidades)

    mensagem = texto_noticias + "\n\n" + texto_analise

    enviar_telegram(mensagem)

# ==============================
# LOOP PRINCIPAL (RODA PRA SEMPRE)
# ==============================

while True:
    try:
        print("Rodando análise...")
        enviar_relatorio()
        print("Enviado com sucesso!")
    except Exception as e:
        print("Erro:", e)

    time.sleep(1800)  # 30 minutos
