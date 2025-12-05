# app_intexta_inventario.py — Consultor de Inventario (prioriza marca + ubicación)
# Reqs: pip install Flask twilio requests pandas

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests, logging, re, json, unicodedata
import pandas as pd
from io import StringIO
from collections import defaultdict, deque

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- Config ---
GSHEET_URL_RAW = "https://docs.google.com/spreadsheets/d/TU_ID/edit#gid=0"  # TODO: cambia TU_ID
DEEPSEEK_API_KEY = "sk-a88ff10322bb40d4ba061536743f4e00"
DEEPSEEK_ENDPOINTS = [
    "https://api.deepseek.com/chat/completions",
    "https://api.deepseek.com/v1/chat/completions",
]

MAX_DOC_CHARS = 12000
MAX_WELCOME_CHARS = 900
HISTORY_TURNS = 12

SESS = defaultdict(lambda: {"history": deque(maxlen=HISTORY_TURNS)})

# --- Utils de normalización ---
def norm_str(s: str) -> str:
    if s is None: return ""
    s = str(s).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

# --- Google Sheets helpers ---
def to_sheet_export_csv(url: str) -> str:
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_\-]+)", url)
    if not m: return url
    file_id = m.group(1)
    gid_m = re.search(r"[?&#]gid=(\d+)", url)
    gid = f"&gid={gid_m.group(1)}" if gid_m else ""
    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv{gid}"

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]
    needed = ["SKU","Nombre","Bodega_Ubicacion_Comuna","Caracteristica","Precio_CLP"]
    for col in needed:
        if col not in df.columns:
            df[col] = None
    df = df[needed]
    # derivar "Marca" del primer token de "Nombre"
    df["Marca"] = df["Nombre"].astype(str).str.strip().str.extract(r"^([A-Za-zÀ-ÿ0-9\-_]+)")[0]
    # normalizados para matcheo
    df["Marca_norm"] = df["Marca"].apply(norm_str)
    df["Bodega_norm"] = df["Bodega_Ubicacion_Comuna"].apply(norm_str)
    return df

def parse_price(val) -> int | None:
    if pd.isna(val): return None
    s = str(val).lower().replace("$"," ").replace("clp"," ").strip()
    s = s.replace(".", "").replace(",", "")
    if "k" in s:
        s = s.replace("k","")
        return int(float(s)*1000) if s else None
    if "mil" in s:
        s = s.replace("mil","").strip()
        return int(float(s)*1000) if s else None
    digits = re.sub(r"\D","", s)
    return int(digits) if digits else None

def load_inventory_df() -> pd.DataFrame:
    url = to_sheet_export_csv(GSHEET_URL_RAW)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text)).dropna(how="all")
    df = normalize_columns(df)
    df["PrecioN"] = df["Precio_CLP"].apply(parse_price)
    df["SKU"] = df["SKU"].astype(str).str.strip()
    return df

def format_price(n: int | None) -> str:
    if n is None: return "N/D"
    return f"${n:,}".replace(",", ".")

def df_to_text(df: pd.DataFrame, limit=40) -> str:
    # muestra Marca derivada y Bodega
    cols = ["SKU","Marca","Nombre","Bodega_Ubicacion_Comuna","Caracteristica"]
    view = df[cols].head(limit).copy()
    view.insert(5, "Precio", df["PrecioN"].head(limit).apply(format_price))
    txt = view.to_string(index=False)
    return txt[:MAX_DOC_CHARS]

# --- Resumen por bodega ---
def bodega_summary_text(df: pd.DataFrame, limit=50) -> str:
    if df.empty: return "No hay datos."
    g = df.groupby("Bodega_Ubicacion_Comuna").agg(
        items=("SKU","count"),
        skus=("SKU", pd.Series.nunique),
        total_valor=("PrecioN","sum")
    ).reset_index().sort_values("items", ascending=False)
    g["total_valor"] = g["total_valor"].fillna(0).astype(int)
    lines = []
    for _, r in g.head(limit).iterrows():
        total_fmt = format_price(r["total_valor"])
        lines.append(f"- {r['Bodega_Ubicacion_Comuna']}: {r['items']} ítems, {r['skus']} SKUs, valor {total_fmt}")
    return "\n".join(lines)

# --- Extractores de filtros (añadimos marca + ubicación como prioridad) ---
def money_to_int(token: str) -> int | None:
    s = token.lower().replace("$"," ").strip()
    s = s.replace(".", "").replace(",", "")
    if "k" in s: return int(float(s.replace("k",""))*1000) if s.replace("k","") else None
    if "mil" in s: return int(float(s.replace("mil",""))*1000) if s.replace("mil","") else None
    digits = re.sub(r"\D","", s)
    return int(digits) if digits else None

def extract_price_range(q: str) -> tuple[int|None,int|None]:
    t = q.lower()
    m = re.search(r"(?:entre|de)\s+([$\d\.\s,k]+)\s+(?:a|y)\s+([$\d\.\s,k]+)", t)
    if m:
        p1, p2 = money_to_int(m.group(1)), money_to_int(m.group(2))
        if p1 and p2: return (min(p1,p2), max(p1,p2))
    m = re.search(r"(?:hasta|máximo|maximo|menos\s+de)\s+([$\d\.\s,k]+)", t)
    if m: return (None, money_to_int(m.group(1)))
    m = re.search(r"(?:desde|mínimo|minimo|más\s+de)\s+([$\d\.\s,k]+)", t)
    if m: return (money_to_int(m.group(1)), None)
    nums = [money_to_int(x) for x in re.findall(r"[$\d][\d\.\s,k]*", t)]
    nums = [n for n in nums if n]
    if len(nums)>=2: return (min(nums[:2]), max(nums[:2]))
    if len(nums)==1: return (None, nums[0])
    return (None,None)

def extract_sku(q: str) -> str | None:
    m = re.search(r"\bsku[:\s\-]*([A-Za-z0-9\-_/]+)", q, re.IGNORECASE)
    return m.group(1).strip() if m else None

def match_catalog(query: str, values: list[str]) -> str | None:
    qn = norm_str(query)
    # match exact por palabra o contains; devuelve el primero que aparezca
    for v in values:
        vn = norm_str(v)
        if not vn: continue
        if re.search(rf"\b{re.escape(vn)}\b", qn) or (vn in qn):
            return v
    return None

def extract_brand(q: str, brands_list: list[str]) -> str | None:
    return match_catalog(q, brands_list)

def extract_bodega(q: str, bodegas_list: list[str]) -> str | None:
    # primero intenta con palabra clave 'bodega/ubicación/comuna'
    m = re.search(r"(?:bodega|ubicaci[oó]n|comuna)\s*[:\-]?\s*([\w\s\-\.,]+)", q, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        hit = match_catalog(val, bodegas_list)
        if hit: return hit
    # si no hubo, busca match directo del texto contra el catálogo
    return match_catalog(q, bodegas_list)

def apply_filters(df: pd.DataFrame, q: str, brands: list[str], bodegas: list[str]) -> pd.DataFrame:
    if df.empty: return df.copy()
    out = df.copy()

    # prioridad: marca y ubicación
    brand = extract_brand(q, brands)
    if brand:
        out = out[out["Marca_norm"] == norm_str(brand)]

    bodega = extract_bodega(q, bodegas)
    if bodega:
        out = out[out["Bodega_norm"] == norm_str(bodega)]

    # filtros adicionales
    sku = extract_sku(q)
    if sku:
        out = out[out["SKU"].str.lower().str.contains(sku.lower())]

    # keywords sobre Nombre/Caracteristica
    t = q.lower()
    for kw in re.findall(r"[a-zA-Z0-9\-\+]{3,}", t):
        if kw in {"sku","bodega","ubicacion","ubicación","comuna","entre","hasta","desde","maximo","mínimo","minimo","más","mas","de","a","y"}:
            continue
        mask = (
            out["Nombre"].astype(str).str.lower().str.contains(kw) |
            out["Caracteristica"].astype(str).str.lower().str.contains(kw)
        )
        out = out[mask] if mask.any() else out

    pmin, pmax = extract_price_range(q)
    if pmin is not None or pmax is not None:
        out = out[out["PrecioN"].notna()]
        if pmin is not None: out = out[out["PrecioN"] >= pmin]
        if pmax is not None: out = out[out["PrecioN"] <= pmax]

    if "PrecioN" in out.columns:
        out = out.sort_values("PrecioN", ascending=True)
    return out

# --- Prompt (system + context) ---
SYSTEM_PROMPT = """
Eres Intexta 🤖, un asistente de inventario.

• Responde en español CL, 1–5 líneas (≤1000 chars), directo y preciso.
• Usa solo datos del inventario (SKU, Nombre, Bodega_Ubicacion_Comuna, Caracteristica, Precio_CLP).
• Prioriza respuesta por MARCA y UBICACIÓN cuando estén presentes.
• Si piden resumen por bodega: ítems, SKUs y valor total.
• Si no hay datos: “❌ No lo encuentro en tus documentos”.
""".strip()

WELCOME_CONTEXT = """
¡Bienvenido/a!
🤖 Soy Intexta. Puedo buscar por MARCA y UBICACIÓN (bodega/comuna), además de SKU, nombre, característica y rango de precio.
También entrego resumen por bodega (ítems, SKUs, valor).
¿En qué te ayudo? 😊
""".strip()

def build_system_msg():
    return {"role": "system", "content": SYSTEM_PROMPT[:1800]}

def build_context_msg(results_block: str, resumen_bodega: str):
    welcome = WELCOME_CONTEXT[:MAX_WELCOME_CHARS]
    docs = (results_block or "Sin resultados").strip()
    bodegas = (resumen_bodega or "Sin datos").strip()
    content = f"""{welcome}

[RESUMEN_BODEGAS]
{bodegas}

[RESULTADOS_FILTRADOS]
{docs}
"""
    return {"role": "system", "content": content[:MAX_DOC_CHARS]}

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

def chunk(s: str, n=1300):
    s = s or "(respuesta vacía)"
    return [s[i:i+n] for i in range(0, len(s), n)]

# --- Carga inventario ---
try:
    DF = load_inventory_df()
    RESUMEN_BODEGA = bodega_summary_text(DF, limit=80)
    INVENTARIO_TXT = df_to_text(DF, limit=120)
    BRANDS_LIST = sorted([x for x in DF["Marca"].dropna().unique().tolist() if str(x).strip()])
    BODEGAS_LIST = sorted([x for x in DF["Bodega_Ubicacion_Comuna"].dropna().unique().tolist() if str(x).strip()])
    logging.info("[INFO] Inventario filas=%d, marcas=%d, bodegas=%d", len(DF), len(BRANDS_LIST), len(BODEGAS_LIST))
except Exception as e:
    logging.exception("[ERROR] Carga inventario: %s", e)
    DF = pd.DataFrame(columns=["SKU","Nombre","Bodega_Ubicacion_Comuna","Caracteristica","Precio_CLP","PrecioN","Marca","Marca_norm","Bodega_norm"])
    RESUMEN_BODEGA = "No hay datos."
    INVENTARIO_TXT = "No hay datos."
    BRANDS_LIST, BODEGAS_LIST = [], []

# --- Endpoints ---
@app.route("/", methods=["GET"])
def health():
    return Response("ok", mimetype="text/plain")

@app.route("/whatsapp", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def webhook():
    user = (request.form.get("From") or "unknown").strip()
    text = (request.form.get("Body") or "").strip()
    logging.info("[MSG] from=%s text='%s'", user, text)

    # aplica brand + ubicación primero
    filtered = apply_filters(DF, text, BRANDS_LIST, BODEGAS_LIST)
    results_block = df_to_text(filtered.head(40), limit=40) if not filtered.empty else "Sin coincidencias para tu filtro."
    bodegas_block = RESUMEN_BODEGA

    SESS[user]["history"].append({"role": "user", "content": text})

    system_msg = build_system_msg()
    context_msg = build_context_msg(results_block, bodegas_block)
    messages = [system_msg, context_msg] + list(SESS[user]["history"])

    answer = call_deepseek(messages, max_tokens=256, temperature=0.2)
    SESS[user]["history"].append({"role": "assistant", "content": answer})

    resp = MessagingResponse()
    for part in chunk(answer, 1300): resp.message(part)
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    # Apunta Twilio a /webhook (POST)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
