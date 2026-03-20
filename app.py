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
# TELEGRAM
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
# CORRIGIR SERIES (ERRO FLOAT)
# ==============================

def ajustar_serie(col):
    if col is None:
        return None

    # Se vier como DataFrame (multi-coluna)
    if hasattr(col, "columns"):
        col = col.iloc[:, 0]

    # Garantir numérico
    col = col.squeeze()

    return col

# ==============================
# DADOS COM FALLBACK
# ==============================

def get_dados(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if data.empty:
            raise Exception

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
# ANÁLISE PROFISSIONAL
# ==============================

def analisar_ativo(ticker):
    try:
        data = get_dados(ticker)

        if data is None or len(data) < 50:
            return None

        close = ajustar_serie(data.get("Close"))
        volume = ajustar_serie(data.get("Volume"))

        if close is None or volume is None:
            return None

        # Garantir valores escalares
        close = close.dropna()
        volume = volume.dropna()

        if len(close) < 30:
            return None

        mm9 = close.rolling(9).mean()
        mm21 = close.rolling(21).mean()

        # Tendência
        tendencia = "ALTA 📈" if mm9.iloc[-1] > mm21.iloc[-1] else "BAIXA 📉"

        # Volume
        vol_atual = float(volume.iloc[-1])
        vol_media = float(volume.rolling(20).mean().iloc[-1])

        volume_status = "FORTE 🔥" if vol_atual > vol_media else "FRACO 💤"

        # Variação
        preco_atual = float(close.iloc[-1])
        preco_anterior = float(close.iloc[-2])

        variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

        # Fluxo
        if variacao > 1:
            fluxo = "COMPRA 🟢"
        elif variacao < -1:
            fluxo = "VENDA 🔴"
        else:
            fluxo = "NEUTRO ⚪"

        return {
            "ticker": ticker.replace(".SA", ""),
            "preco": round(preco_atual, 2),
            "variacao": round(variacao, 2),
            "tendencia": tendencia,
            "volume": volume_status,
            "fluxo": fluxo
        }

    except Exception as e:
        print(f"Erro análise {ticker}: {e}")
        return None

# ==============================
# SCANNER
# ==============================

def scanner_b3():
    resultados = []

    for ativo in ATIVOS:
        r = analisar_ativo(ativo)
        if r:
            resultados.append(r)

    oportunidades = [
        r for r in resultados
        if r["fluxo"] == "COMPRA 🟢" and r["volume"] == "FORTE 🔥"
    ]

    return resultados, oportunidades

# ==============================
# NOTÍCIAS
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
# FORMATAR COTAÇÕES
# ==============================

def formatar_cotacoes(resultados):
    texto = "💰 *COTAÇÕES DAS AÇÕES*\n\n"

    for r in resultados:
        emoji = "🟢" if r["variacao"] > 0 else "🔴"

        texto += f"{emoji} *{r['ticker']}* → R$ {r['preco']} ({r['variacao']}%)\n"

    return texto + "\n━━━━━━━━━━━━━━━\n\n"

# ==============================
# FORMATAR ANÁLISE
# ==============================

def formatar_analises(resultados):
    texto = "📊 *ANÁLISE INSTITUCIONAL*\n\n"

    for r in resultados:
        texto += (
            f"🏢 *{r['ticker']}*\n"
            f"📈 {r['tendencia']} | {r['fluxo']}\n"
            f"📊 Volume: {r['volume']}\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
        )

    return texto

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
# RELATÓRIO FINAL
# ==============================

def enviar_relatorio():
    resultados, _ = scanner_b3()
    noticias = buscar_noticias()

    msg = (
        formatar_cotacoes(resultados) +
        formatar_analises(resultados) +
        "\n" +
        formatar_noticias(noticias)
    )

    enviar_telegram(msg)

# ==============================
# LOOP
# ==============================

while True:
    try:
        print("Rodando robô...")
        enviar_relatorio()
        print("Enviado com sucesso!")
    except Exception as e:
        print("Erro geral:", e)

    time.sleep(1800)
