from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import pandas as pd
import json
import re

app = Flask(__name__)

GSHEET_URL = "https://docs.google.com/spreadsheets/d/1athLB97eeel00E0ies7Yf1FByNWUnvRUAwCHSSJsYkA/export?format=csv"
DEEPSEEK_API_KEY = "sk-c325605e00924a1ea48459214b22f56f"

conversaciones = {}
transacciones = {}
df = pd.read_csv(GSHEET_URL)

def analizar_mensaje(user_id):
    sistema_prompt = (
        "Eres un asistente experto en inventario electrónico. Siempre respondes en JSON válido con campos: "
        "intencion, tipo, marca, modelo, color, pregunta_extra. "
        "Puedes seguir el contexto de lo que el usuario viene conversando. "
        "Pregunta_extra detecta si el usuario dice '¿tienes otro color?', '¿cuántos quedan?', '¿la otra opción más barata?', 'quiero comprarlo'."
    )
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": sistema_prompt}] + conversaciones[user_id]
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        print("[DeepSeek RAW]", r.text)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        conversaciones[user_id].append({"role": "assistant", "content": content})
        match = re.search(r"\{[\s\S]*?\}", content)
        if match:
            json_str = match.group(0)
            print("[DeepSeek Cleaned]", json_str)
            return json.loads(json_str)
        else:
            raise ValueError("No se encontró JSON válido en la respuesta.")
    except Exception as e:
        print("[ERROR] DeepSeek:", e)
        return {"intencion": None, "tipo": None, "marca": None, "modelo": None, "color": None, "pregunta_extra": None}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '')
    user_id = request.form.get('From')

    if user_id not in conversaciones:
        conversaciones[user_id] = []
    if user_id not in transacciones:
        transacciones[user_id] = {"estado": None, "datos": {}}

    conversaciones[user_id].append({"role": "user", "content": incoming_msg})
    estado = transacciones[user_id]["estado"]

    if estado == "esperando_pago":
        transacciones[user_id]["datos"]["pago"] = incoming_msg
        transacciones[user_id]["estado"] = "esperando_entrega"
        respuesta = "¿Deseas despacho a domicilio o retiro en tienda?"
    elif estado == "esperando_entrega":
        transacciones[user_id]["datos"]["entrega"] = incoming_msg
        datos = transacciones[user_id]["datos"]
        respuesta = f"✅ Compra confirmada.\nProducto: {datos.get('producto','?')}\nPago: {datos.get('pago','?')}\nEntrega: {datos.get('entrega','?')}\nGracias por tu compra. Esta es tu boleta."
        transacciones[user_id] = {"estado": None, "datos": {}}  # reiniciar
    else:
        criterios = analizar_mensaje(user_id)
        intencion = criterios.get("intencion")
        tipo = criterios.get("tipo")
        marca = criterios.get("marca")
        modelo = criterios.get("modelo")
        color = criterios.get("color")
        pregunta_extra = criterios.get("pregunta_extra")
        respuesta = ""

        # Normalización de tipo
        sinonimos_tipo = {
            "celular": "Teléfono",
            "movil": "Teléfono",
            "móvil": "Teléfono",
            "smartphone": "Teléfono",
            "telefono": "Teléfono",
            "teléfono": "Teléfono"
        }
        if tipo in sinonimos_tipo:
            tipo = sinonimos_tipo[tipo]

        if intencion == "saludo":
            respuesta = "¡Hola! Bienvenido/a a la tienda de Synapse Technologies. ¿En qué puedo ayudarte hoy?"
        elif pregunta_extra == "otro_color":
            respuesta = "Claro, ¿qué otro color te gustaría que busque?"
        elif pregunta_extra == "cuantos_quedan":
            respuesta = "Permíteme verificar el stock exacto y te confirmo cuántos quedan."
        elif pregunta_extra == "opcion_mas_barata":
            respuesta = "Voy a buscar la opción más económica disponible."
        elif any(frase in incoming_msg.lower() for frase in ["quiero comprarlo", "sí", "si quiero ese", "ya", "lo quiero", "me interesa","vale", "esta bien","ok"]):
            transacciones[user_id]["estado"] = "esperando_pago"
            producto = conversaciones[user_id][-2]["content"] if len(conversaciones[user_id]) >= 2 else "[producto no identificado]"
            transacciones[user_id]["datos"]["producto"] = producto
            respuesta = "Perfecto, introduce una tarjeta, fecha de vencimiento y el código de seguridad."
        elif intencion in ["general", "compra"]:
            filtro = df
            if tipo: filtro = filtro[filtro["Tipo"].str.lower() == tipo.lower()]
            if marca: filtro = filtro[filtro["Marca"].str.lower() == marca.lower()]
            if color: filtro = filtro[filtro["Color"].str.lower() == color.lower()]
            resultado = filtro.head(5)
            if resultado.empty:
                respuesta = "No encontré productos con esos criterios."
            else:
                respuesta = "Aquí tienes algunos ejemplos:\n" + "\n".join(
                    f"- {r['Marca']} {r['Modelo']} ({r['Color']}, stock: {r['Cantidad']})" for _, r in resultado.iterrows())
        elif intencion == "concreta" and modelo:
            filtro = df[df["Modelo"].str.lower() == modelo.lower()]
            if color: filtro = filtro[filtro["Color"].str.lower() == color.lower()]
            if filtro.empty:
                respuesta = f"No encontré el {modelo}."
            else:
                r = filtro.iloc[0]
                respuesta = f"Entonces quieres el {r['Modelo']} {r['Color']} que tiene un valor de ${r['Precio']}."
        else:
            respuesta = "No entendí tu consulta. Puedes preguntar por tipo, marca, modelo, color o detalles adicionales."

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(respuesta)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
