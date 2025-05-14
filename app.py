
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
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente experto en analizar uñas a partir de imágenes. "
                        "Debes identificar la forma de la uña (almendra, cuadrada, coffin), "
                        "técnicas base y decoraciones visibles como french, pedrería, baby boomer, "
                        "glitter, efecto dorado, mármol, corazones, mano alzada, 3D, ojo de gato. "
                        "Di cuántas uñas tienen cada decoración."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analiza esta imagen. Tamaño de uña: #{tamano}."},
                        {"type": "image_url", "image_url": {"url": imagen, "detail": "low"}}
                    ]
                }
            ]
        )

        descripcion = response.choices[0].message.content.lower()
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
                if cantidad == 0:
                    cantidad = 1
                total += precio * cantidad
                desglose.append(f"{extra.capitalize()} x{cantidad}: ${precio * cantidad}")

        desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

        return jsonify({
            "descripcion": descripcion,
            "resultado": "\n".join(desglose)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/corregir", methods=["POST"])
def corregir():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 401

    elementos = data.get("elementos", {})
    tamano = str(data.get("tamano", "5"))
    total = 0
    desglose = []

    if tamano in PRECIOS["tamanos"]:
        precio_tamano = PRECIOS["tamanos"][tamano]
        total += precio_tamano
        desglose.append(f"Tamaño de uña #{tamano}: ${precio_tamano}")

    forma = elementos.get("forma")
    if forma in PRECIOS["formas"]:
        total += PRECIOS["formas"][forma]
        desglose.append(f"Forma {forma}: ${PRECIOS['formas'][forma]}")

    extras = elementos.get("extras", {})
    for extra, cantidad in extras.items():
        if extra in PRECIOS["extras"]:
            subtotal = PRECIOS["extras"][extra] * cantidad
            total += subtotal
            desglose.append(f"{extra.capitalize()} x{cantidad}: ${subtotal}")

    desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

    return jsonify({
        "resultado": "\n".join(desglose)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
