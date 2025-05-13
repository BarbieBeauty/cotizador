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
                {"role": "system", "content": "Eres un asistente experto en analizar imágenes de uñas. Detecta con precisión: forma (almendra, cuadrada, coffin), técnica base, y decoraciones como french, mármol, glitter, pedrería, etc. Especifica cantidad de uñas por decoración si es posible."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe visualmente esta imagen. Tamaño de uña: #{tamano}."},
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

        for forma, precio in PRECIOS["formas"].items():
            if forma in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        for extra, precio in PRECIOS["extras"].items():
            if extra in descripcion:
                cantidad = 1
                for i in range(1, 11):
                    if f"{extra} x{i}" in descripcion or f"{i} uñas con {extra}" in descripcion:
                        cantidad = i
                        break
                if extra in ["pedrería chica", "glitter", "french", "mármol", "efecto dorado", "corazones", "ojo de gato", "3d"]:
                    cantidad = max(cantidad, 4)
                total += precio * cantidad
                desglose.append(f"{extra.capitalize()} x{cantidad}: ${precio * cantidad}")

        desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

        return jsonify({
            "descripcion": descripcion,
            "resultado": "\n".join(desglose)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
