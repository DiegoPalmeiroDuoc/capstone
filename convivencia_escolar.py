from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests, logging, re
from requests.adapters import HTTPAdapter, Retry

# —— Intento de usar BeautifulSoup; si no está, caemos a un fallback de regex ——
try:
    from bs4 import BeautifulSoup  # pip install beautifulsoup4 lxml
    HAS_BS4 = True
except Exception:
    HAS_BS4 = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# —— CONFIG —— (tu link /edit tal cual, sin export)
GOOGLE_DOC_EDIT_URL = "https://docs.google.com/document/d/1n2mAoHE15wzvmOm01Aq1AB7Mf5-hgM64v5Zg2t_SaCQ/edit?usp=sharing"
DEEPSEEK_API_KEY = "sk-8b870bc10d534b0786baa18510739493"

# —— Sesión HTTP robusta (reintentos + User-Agent) ——
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"})
retries = Retry(total=3, backoff_factor=0.6, status_forcelist=[429,500,502,503,504],
                allowed_methods=frozenset(["GET","POST"]))
adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=20)
session.mount("https://", adapter)
session.mount("http://", adapter)

def html_to_text(html: str) -> str:
    """Convierte HTML grande en texto plano. Usa bs4 si existe; si no, regex fallback."""
    if HAS_BS4:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
    else:
        # Fallback simple si no hay bs4/lxml
        text = re.sub(r"(?is)<(script|style).*?</\1>", "", html)  # quita scripts/styles
        text = re.sub(r"(?is)<[^>]+>", "\n", text)               # quita tags
    # Normaliza espacios y líneas vacías
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    text = "\n".join(lines)
    return text

def fetch_doc_text_from_edit(url: str) -> str:
    """Descarga el HTML del /edit. Si no es público, Google redirige a login."""
    r = session.get(url, timeout=30, allow_redirects=True)
    logging.info("[INFO] GET %s -> %s (final=%s)", url, r.status_code, r.url)
    if "accounts.google.com" in r.url:
        return ("Documento no accesible sin login. Ajustar a 'Cualquier persona con el enlace'.")
    r.raise_for_status()
    txt = html_to_text(r.text)
    logging.info("Texto limpio: %d caracteres (antes de seleccionar fragmentos).", len(txt))
    return txt

def select_relevant(text: str, query: str, window_chars: int = 900, max_chars: int = 20000) -> str:
    """
    Extrae ventanas de texto alrededor de palabras clave de la consulta.
    Limita el total para no exceder contexto del modelo.
    """
    if not text:
        return ""
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) >= 4]
    if not words:
        return text[:max_chars]

    lc = text.lower()
    positions = []
    for w in words:
        for m in re.finditer(re.escape(w), lc):
            positions.append(m.start())
    if not positions:
        return text[:max_chars]

    positions = sorted(set(positions))
    chunks, last_end = [], -1
    for pos in positions[:30]:  # límite de ventanas
        start = max(0, pos - window_chars)
        end = min(len(text), pos + window_chars)
        if chunks and start <= last_end:  # unir solapes
            prev_start, prev_end = chunks[-1]
            chunks[-1] = (prev_start, max(prev_end, end))
            last_end = chunks[-1][1]
        else:
            chunks.append((start, end))
            last_end = end

    parts, acc = [], 0
    for start, end in chunks:
        seg = text[start:end].strip()
        if not seg:
            continue
        if acc + len(seg) + 100 > max_chars:
            seg = seg[:max(0, max_chars - acc)]
            parts.append(seg)
            break
        parts.append(seg)
        acc += len(seg) + 1
        if acc >= max_chars:
            break

    out = "\n---\n".join(parts).strip() or text[:max_chars]
    logging.info("Fragmento seleccionado: %d caracteres (tope=%d).", len(out), max_chars)
    return out

def deepseek_chat(prompt: str) -> dict:
    """Llama a DeepSeek con fallback de endpoint, header 'Bearer' correcto y límite de tokens."""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Responde solo basado en el texto provisto. Máx 3 frases, en español."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512
    }
    endpoints = ["https://api.deepseek.com/chat/completions", "https://api.deepseek.com/v1/chat/completions"]
    last_exc = None
    for url in endpoints:
        try:
            r = session.post(url, json=payload, headers=headers, timeout=40)
            logging.info("[DeepSeek] %s -> %s", url, r.status_code)
            if r.status_code >= 400:
                logging.error("[DeepSeek] body=%s", r.text[:1500])
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last_exc = exc
            continue
    logging.exception("DeepSeek falló en ambos endpoints: %s", last_exc)
    return {"choices": [{"message": {"content": "No se pudo contactar al modelo."}}], "usage": {}}

def chunk_text(s: str, size: int = 1300):
    if not s:
        return ["(respuesta vacía)"]
    return [s[i:i + size] for i in range(0, len(s), size)]

@app.route("/", methods=["GET"])
def health():
    return Response("ok", mimetype="text/plain")

@app.route("/whatsapp", methods=["POST"])
@app.route("/webhook", methods=["POST"])  # alias por si Twilio apunta a /webhook
def whatsapp_reply():
    logging.info("[REQ] %s %s form=%s", request.method, request.path, dict(request.form))
    incoming_msg = (request.form.get("Body") or "").strip()

    # 1) Leer HTML del /edit y convertir a texto
    full_text = fetch_doc_text_from_edit(GOOGLE_DOC_EDIT_URL)

    # 2) Elegir fragmentos relevantes y limitar tamaño
    relevant = select_relevant(full_text, incoming_msg, window_chars=900, max_chars=20000)

    # 3) Prompt compacto
    prompt = f"""Texto de referencia (recortado y limpiado):
{relevant}

Pregunta del usuario:
{incoming_msg}
"""

    # 4) Llamar a DeepSeek
    resp_json = deepseek_chat(prompt)
    try:
        answer = (resp_json["choices"][0]["message"]["content"] or "").strip()
        if not answer:
            raise ValueError("contenido vacío")
    except Exception:
        answer = "Lo siento, hubo un problema al procesar la respuesta."

    # 5) Responder en partes para WhatsApp
    twiml = MessagingResponse()
    for part in chunk_text(answer, size=1300):
        twiml.message(part)
    return Response(str(twiml), mimetype="application/xml")

if __name__ == "__main__":
    # Ejecuta: python convivencia_escolar.py
    # Apunta Twilio a https://<ngrok>.ngrok.io/webhook (o /whatsapp)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
