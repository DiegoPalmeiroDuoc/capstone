from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Link directo para exportar Google Docs como TXT
GOOGLE_DOC_TXT_EXPORT = "https://docs.google.com/document/d/1phVw-i45SCCmfWQjKHMKnNHI0-qR03sH-P-kLGeZs44/export?format=txt"

def load_file_content():
    try:
        r = requests.get(GOOGLE_DOC_TXT_EXPORT)
        r.raise_for_status()
        print("[INFO] Archivo cargado correctamente desde Google Docs.")
        return r.text
    except Exception as e:
        print("[ERROR] No se pudo cargar el archivo:", e)
        return "No se pudo cargar el archivo de Google Docs."

# Inicializar
file_content = load_file_content()

@app.route("/whatsapp", methods=["POST"])
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body') or ""
    
    prompt = f"""
Eres un asistente experto. A continuación tienes el contenido del archivo:

{file_content}

Pregunta del usuario: {incoming_msg}

Responde de forma breve, basada solo en el archivo, usando máximo 3 frases.
"""

    response = call_deepseek_api(prompt)
    print("[INFO] DeepSeek JSON:", response)

    # Obtener respuesta
    try:
        answer = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        print("[ERROR] Al extraer respuesta:", e)
        answer = "Lo siento, hubo un problema al procesar la respuesta del modelo."

    # Mostrar tokens
    usage = response.get("usage", {})
    print(f"[TOKENS] prompt_tokens: {usage.get('prompt_tokens', '?')}, "
          f"completion_tokens: {usage.get('completion_tokens', '?')}, "
          f"total_tokens: {usage.get('total_tokens', '?')}")

    # Responder por WhatsApp
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(answer)
    print("Twilio XML response:", str(resp))
    return str(resp)

def call_deepseek_api(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-5d84c8f184c14de89a58c5c4da59889a",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        print("[INFO] DeepSeek status code:", r.status_code)
        print("[INFO] DeepSeek raw text:", r.text)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("[ERROR] Al llamar a DeepSeek:", e)
        return {"choices": [{"message": {"content": "Lo siento, hubo un problema con la API."}}]}

if __name__ == "__main__":
    app.run(port=5000, debug=True)
