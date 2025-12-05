# app_intexta_continuo.py — WhatsApp (Twilio) + DeepSeek con memoria y filtros (marca/modelo/capacidad/precio)
# Reqs: pip install Flask twilio requests pandas

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests, logging, re, json
import pandas as pd
from io import StringIO
from collections import defaultdict, deque

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- Config ---
GSHEET_URL_RAW = "https://docs.google.com/spreadsheets/d/1-YjcSOIieEFzV--iDdEAxlY4Cfn3NKioGGG8bwAsgns/edit?gid=94165952#gid=94165952"
DEEPSEEK_API_KEY = "sk-a88ff10322bb40d4ba061536743f4e00"

MAX_DOC_CHARS = 12000
MAX_WELCOME_CHARS = 1000
HISTORY_TURNS = 12

SESS = defaultdict(lambda: {
    "history": deque(maxlen=HISTORY_TURNS),
    "flow": {
        "stage": "idle",
        "producto": None,
        "tarjeta_mask": None,
        "vencimiento": None,
        "cvv": None,
        "envio": None,
        "direccion": None
    }
})

DEEPSEEK_ENDPOINTS = [
    "https://api.deepseek.com/chat/completions",
    "https://api.deepseek.com/v1/chat/completions",
]

# --- Google Sheets helpers ---
def to_sheet_export_csv(url: str) -> str:
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_\-]+)", url)
    if not m: return url
    file_id = m.group(1)
    gid_m = re.search(r"[?&#]gid=(\d+)", url)
    gid = f"&gid={gid_m.group(1)}" if gid_m else ""
    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv{gid}"

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().capitalize() for c in df.columns]
    map_cols = {
        "producto":"Modelo","nombre":"Modelo","modelo":"Modelo",
        "marca":"Marca","color":"Color","tipo":"Tipo",
        "precio":"Precio","valor":"Precio",
        "cantidad":"Cantidad","stock":"Cantidad","existencia":"Cantidad",
        "capacidad":"Almacenamiento","almacenamiento":"Almacenamiento","storage":"Almacenamiento"
    }
    ren = {}
    for col in df.columns:
        k = col.lower().strip()
        if k in map_cols: ren[col] = map_cols[k]
    return df.rename(columns=ren)

def parse_gb(val) -> float | None:
    if pd.isna(val): return None
    s = str(val).lower().strip()
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(tb|gb)\b", s)
    if m:
        num = float(m.group(1).replace(",", "."))
        unit = m.group(2)
        return round(num*1024,2) if unit=="tb" else round(num,2)
    m2 = re.search(r"\b(\d+)\b", s)
    return float(m2.group(1)) if m2 else None

def parse_price(val) -> int | None:
    if pd.isna(val): return None
    s = str(val).lower().replace("$"," ").replace("clp"," ").strip()
    s = s.replace(".", "").replace(",", "")
    if "k" in s: 
        s = s.replace("k","")
        return int(float(s)*1000) if s.strip().isdigit() else None
    if "mil" in s:
        s = s.replace("mil","").strip()
        return int(float(s)*1000) if s and s.replace(".","").isdigit() else None
    digits = re.sub(r"\D","", s)
    return int(digits) if digits else None

def format_price(n: int) -> str:
    if n is None: return "N/D"
    return f"${n:,}".replace(",", ".")

def load_inventory_df() -> pd.DataFrame:
    export_url = to_sheet_export_csv(GSHEET_URL_RAW)
    r = requests.get(export_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, allow_redirects=True)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text)).dropna(how="all")
    df = normalizar_columnas(df)
    # set columnas base
    for col in ["Tipo","Marca","Modelo","Color","Almacenamiento","Precio","Cantidad"]:
        if col not in df.columns: df[col] = None
    # numéricos
    df["AlmacenamientoGB"] = df["Almacenamiento"].apply(parse_gb)
    df["PrecioN"] = df["Precio"].apply(parse_price)
    return df

def df_to_compact_text(df: pd.DataFrame, limit=100) -> str:
    cols = [c for c in ["Tipo","Marca","Modelo","Color","Almacenamiento","Precio","Cantidad"] if c in df.columns]
    view = df[cols].head(limit).copy()
    # imprime precio formateado si existe PrecioN
    if "Precio" in view.columns and "PrecioN" in df.columns:
        view["Precio"] = df.loc[view.index, "PrecioN"].apply(format_price)
    txt = view.to_string(index=False)
    return txt[:MAX_DOC_CHARS]

try:
    INVENTORY_DF = load_inventory_df()
    INVENTORY_TEXT = df_to_compact_text(INVENTORY_DF, limit=200)
    BRANDS = {str(x).strip().lower() for x in INVENTORY_DF["Marca"].dropna().unique()}
    MODELS = {str(x).strip().lower() for x in INVENTORY_DF["Modelo"].dropna().unique()}
    logging.info("[INFO] Inventario cargado (%d filas).", len(INVENTORY_DF))
except Exception as e:
    logging.exception("[ERROR] Inventario: %s", e)
    INVENTORY_DF = pd.DataFrame()
    INVENTORY_TEXT = "No se pudo cargar el inventario."
    BRANDS, MODELS = set(), set()

# --- Extractores de filtros ---
def money_to_int(token: str) -> int | None:
    s = token.lower().replace("$"," ").strip()
    s = s.replace(".", "").replace(",", "")
    if "k" in s:
        s = s.replace("k","")
        return int(float(s)*1000) if s else None
    if "mil" in s:
        s = s.replace("mil","")
        return int(float(s)*1000) if s else None
    digits = re.sub(r"\D","", s)
    return int(digits) if digits else None

def extract_price_range(q: str) -> tuple[int|None, int|None]:
    text = q.lower()
    # entre X y Y / de X a Y
    m = re.search(r"(?:entre|de)\s+([$\d\.\s,k]+)\s+(?:a|y)\s+([$\d\.\s,k]+)", text)
    if m:
        p1, p2 = money_to_int(m.group(1)), money_to_int(m.group(2))
        if p1 and p2: return (min(p1,p2), max(p1,p2))
    # hasta Y / máximo Y / menos de Y
    m = re.search(r"(?:hasta|máximo|maximo|menos\s+de)\s+([$\d\.\s,k]+)", text)
    if m:
        p2 = money_to_int(m.group(1))
        return (None, p2)
    # desde X / mínimo X / más de X
    m = re.search(r"(?:desde|mínimo|minimo|más\s+de)\s+([$\d\.\s,k]+)", text)
    if m:
        p1 = money_to_int(m.group(1))
        return (p1, None)
    # dos números sueltos (fallback)
    nums = [money_to_int(x) for x in re.findall(r"[$\d][\d\.\s,k]*", text)]
    nums = [n for n in nums if n]
    if len(nums) >= 2: return (min(nums[:2]), max(nums[:2]))
    if len(nums) == 1: return (None, nums[0])
    return (None, None)

def extract_capacity_range(q: str) -> tuple[float|None, float|None]:
    text = q.lower()
    # 128 a 256 gb
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:gb|gigas?)\s*(?:a|hasta|-|y)\s*(\d+(?:[.,]\d+)?)\s*(?:gb|gigas?)", text)
    if m:
        a = float(m.group(1).replace(",", "."))
        b = float(m.group(2).replace(",", "."))
        return (min(a,b), max(a,b))
    # exacto 128gb
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:gb|gigas?)", text)
    if m:
        v = float(m.group(1).replace(",", "."))
        return (v, v)
    # TB
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*tb", text)
    if m:
        v = float(m.group(1).replace(",", ".")) * 1024
        return (v, v)
    return (None, None)

def detect_brand_model(q: str) -> tuple[str|None, str|None]:
    text = q.lower()
    brand = next((b for b in BRANDS if re.search(rf"\b{re.escape(b)}\b", text)), None)
    model = next((m for m in MODELS if re.search(rf"\b{re.escape(m)}\b", text)), None)
    return (brand, model)

def apply_filters(df: pd.DataFrame, q: str) -> pd.DataFrame:
    if df.empty: return df
    brand, model = detect_brand_model(q)
    pmin, pmax = extract_price_range(q)
    cmin, cmax = extract_capacity_range(q)

    out = df.copy()
    if brand:
        out = out[out["Marca"].str.lower() == brand]
    if model:
        out = out[out["Modelo"].str.lower() == model]
    if cmin is not None and "AlmacenamientoGB" in out.columns:
        out = out[out["AlmacenamientoGB"].notna()]
        if cmax is None: cmax = cmin
        out = out[(out["AlmacenamientoGB"] >= cmin) & (out["AlmacenamientoGB"] <= cmax)]
    if (pmin is not None or pmax is not None) and "PrecioN" in out.columns:
        out = out[out["PrecioN"].notna()]
        if pmin is not None: out = out[out["PrecioN"] >= pmin]
        if pmax is not None: out = out[out["PrecioN"] <= pmax]
    # orden por precio si existe
    if "PrecioN" in out.columns:
        out = out.sort_values("PrecioN", ascending=True)
    return out

# --- Prompt (system + contexto) ---
SYSTEM_PROMPT = """
Eres Intexta 🤖, un asistente virtual experto y amigable.

[IDIOMA]
Responde en español neutro (CL).

📋 TU MISIÓN:
Responder preguntas basándote ÚNICAMENTE en los documentos del usuario (inventario/ETL y materiales proporcionados).

✅ RESPUESTAS IDEALES:
• ULTRA BREVE: Máximo 5 líneas (1000 caracteres MAX).
• DIRECTO AL GRANO.
• RELEVANTE: Solo información útil.
• CONFIABLE: Basado en los documentos del usuario.
• ESPECÍFICO: Solo info exacta.
• AMIGABLE y cercana ✨

❌ EVITA:
• Frases como “Según el documento…”.
• Repetir la pregunta.
• Inventar información.
• Respuestas largas o genéricas.
• Información no sustentada en los documentos.

🎯 SI NO ENCUENTRAS LA INFO:
Responde únicamente: “❌ No lo encuentro en tus documentos”.

💡 FORMATO DE RESPUESTA:
→ Respuesta directa (1–5 líneas).
→ Usa emojis puntuales: 📌 ✓ • 💡

——— DOMINIO: Venta de TELÉFONOS ———
• Usa SOLO lo que esté en los documentos/inventario.
• Listados: hasta 4 modelos por marca, máx 5 en total.
• Filtra por almacenamiento (GB) y por rango de precio cuando se pida.
• Respuestas ≤ 400 caracteres cuando sea posible (nunca >1000).

COMPRA (SIMULACIÓN)
• Recolecta: (1) producto exacto, (2) numero de tarjeta (16 digitos) + MM/YY + 123, (3) envío/dirección.
• Enmascara tarjeta en respuestas: **** **** **** 1111.
• Emite boleta simulada cuando estén los 3.
""".strip()

WELCOME_CONTEXT = """
¡Bienvenido/a!
🤖 Soy Intexta. Seré tu asistente inteligente para encontrar el telefono que mas te guste.
¿En qué te ayudo? 😊
""".strip()

def build_system_msg():
    return {"role": "system", "content": SYSTEM_PROMPT[:1800]}

def build_context_msg(filtered_block: str):
    welcome = WELCOME_CONTEXT[:MAX_WELCOME_CHARS]
    docs = (INVENTORY_TEXT or "")[:MAX_DOC_CHARS]
    ctx = f"{welcome}\n\n[RESULTADOS_FILTRADOS]\n{filtered_block}\n\n[DOCUMENTOS]\n{docs}"
    return {"role": "system", "content": ctx}

# --- Flujo compra parsers ---
CARD_RE = re.compile(r"(?:\D|^)(4111\s?1111\s?1111\s?1111)(?:\D|$)")
EXP_RE  = re.compile(r"(0[1-9]|1[0-2])\s*/\s*(\d{2})")
CVV_RE  = re.compile(r"\b(\d{3})\b")
ENVIO_RE = re.compile(r"\b(domicilio|retiro)\b", re.IGNORECASE)
DIR_RE   = re.compile(r"(?:direccion|dirección|calle)\s*[:\-]?\s*(.+)", re.IGNORECASE)

def update_flow(user: str, text: str):
    flow = SESS[user]["flow"]; low = text.lower()
    if any(x in low for x in ["quiero comprar", "lo compro", "lo quiero", "comprar"]):
        if flow["stage"] == "idle": flow["stage"] = "esperando_producto"
    if flow["stage"] in {"esperando_producto","idle"}:
        if any(k in low for k in ["iphone","samsung","xiaomi","motorola","nokia","huawei","pixel"]):
            flow["producto"] = text.strip()
            if flow["stage"] == "esperando_producto": flow["stage"] = "esperando_tarjeta"
    if CARD_RE.search(text.replace(" ", "")):
        flow["tarjeta_mask"] = "**** **** **** 1111"
        m_exp = EXP_RE.search(text); m_cvv = CVV_RE.search(text)
        if m_exp: flow["vencimiento"] = f"{m_exp.group(1)}/{m_exp.group(2)}"
        if m_cvv: flow["cvv"] = m_cvv.group(1)
        if flow["stage"] in {"esperando_tarjeta","esperando_producto"}: flow["stage"] = "esperando_envio"
    m_env = ENVIO_RE.search(text)
    if m_env: flow["envio"] = m_env.group(1).lower()
    m_dir = DIR_RE.search(text)
    if m_dir: flow["direccion"] = m_dir.group(1).strip()

def flow_complete(flow: dict) -> bool:
    return bool(flow["producto"] and flow["tarjeta_mask"] and flow["envio"] and (flow["envio"]=="retiro" or flow["direccion"]))

# --- LLM client ---
def call_deepseek(messages, max_tokens=256, temperature=0.2) -> str:
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    last_err = None
    for url in DEEPSEEK_ENDPOINTS:
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=40)
            logging.info("[DeepSeek] %s -> %s", url, r.status_code)
            if r.status_code >= 400: logging.error("[DeepSeek] body=%s", r.text[:1200])
            r.raise_for_status()
            data = r.json()
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception as e:
            last_err = e; continue
    logging.exception("DeepSeek falló: %s", last_err)
    return "Lo siento, hubo un problema al contactar el modelo."

def chunks(s: str, n=1300):
    s = s or "(respuesta vacía)"
    return [s[i:i+n] for i in range(0, len(s), n)]

# --- Endpoints ---
@app.route("/", methods=["GET"])
def health():
    return Response("ok", mimetype="text/plain")

@app.route("/whatsapp", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user = (request.form.get("From") or "unknown").strip()
    text = (request.form.get("Body") or "").strip()
    logging.info("[MSG] from=%s text='%s'", user, text)

    # filtros por query (precio/capacidad/marca/modelo)
    filtered_df = apply_filters(INVENTORY_DF, text)
    if not filtered_df.empty:
        filtered_block = df_to_compact_text(filtered_df.head(30), limit=30)
    else:
        filtered_block = "Sin coincidencias con tu filtro. Puedes ajustar marca/modelo/capacidad o precio."

    update_flow(user, text)
    SESS[user]["history"].append({"role": "user", "content": text})

    system_msg = build_system_msg()
    context_msg = build_context_msg(filtered_block)
    flow_snapshot = {"role": "system", "content": f"ESTADO_ACTUAL_JSON={json.dumps(SESS[user]['flow'], ensure_ascii=False)}"}
    messages = [system_msg, context_msg, flow_snapshot] + list(SESS[user]["history"])

    answer = call_deepseek(messages, max_tokens=256, temperature=0.2)
    SESS[user]["history"].append({"role": "assistant", "content": answer})

    resp = MessagingResponse()
    for part in chunks(answer, 1300): resp.message(part)
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
