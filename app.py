
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

PRECIOS = {
    "formas": {"almendra": 50, "cuadrada": 0, "coffin": 50},
    "tamanos": {
        "1": 260, "2": 280, "3": 330, "4": 380, "5": 440,
        "6": 480, "7": 540, "8": 590, "9": 640, "10": 690
    },
    "extras": {
        "french": 10,
        "baby boomer": 15,
        "pedrería chica": 1.5,
        "pedrería grande": 30,
        "glitter": 20,
        "efecto dorado": 15,
        "corazones": 10,
        "mármol": 15,
        "ojo de gato": 5,
        "mano alzada sencilla": 10,
        "mano alzada compleja": 18,
        "3d": 15
    }
}

def analizar_descripcion(descripcion, tamano):
    total = 0
    desglose = []

    if tamano in PRECIOS["tamanos"]:
        precio_tamano = PRECIOS["tamanos"][tamano]
        total += precio_tamano
        desglose.append(f"Tamaño de uña #{tamano}: ${precio_tamano}")

    if "almendra" in descripcion:
        total += PRECIOS["formas"]["almendra"]
        desglose.append("Forma almendra: $50")
    elif "cuadrada" in descripcion:
        total += PRECIOS["formas"]["cuadrada"]
        desglose.append("Forma cuadrada: $0")
    elif "coffin" in descripcion:
        total += PRECIOS["formas"]["coffin"]
        desglose.append("Forma coffin: $50")

    for extra, precio in PRECIOS["extras"].items():
        if extra in descripcion:
            cantidad = descripcion.count(extra)
            total += precio * cantidad
            desglose.append(f"{extra.capitalize()} x{cantidad}: ${precio * cantidad}")

    desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

    return {
        "descripcion": descripcion,
        "resultado": "\n".join(desglose)
    }

@app.route("/analizar", methods=["POST"])
def analizar():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 401

    imagen = data.get("imagen")
    tamano = str(data.get("tamano", "5"))
    if not imagen:
        return jsonify({"error": "Falta la imagen"}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en cotización de uñas. Describe en detalle la forma de la uña, técnica base y todas las decoraciones o efectos visibles como pedrería, glitter, mármol, 3D, etc."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe visualmente esta imagen para cotizar un set de uñas. Tamaño de uña: #{tamano}."},
                        {"type": "image_url", "image_url": {"url": imagen, "detail": "high"}}
                    ]
                }
            ]
        )

        descripcion = response.choices[0].message.content.lower()
        return jsonify(analizar_descripcion(descripcion, tamano))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/corregir", methods=["POST"])
def corregir():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 401

    tamano = str(data.get("tamano", "5"))
    forma = data.get("forma", "")
    extras = data.get("extras", [])  # lista

    descripcion = forma.lower() + " " + " ".join([e.lower() for e in extras])
    return jsonify(analizar_descripcion(descripcion, tamano))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
