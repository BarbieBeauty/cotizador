
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import re

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

TABLAS = {
    "formas": {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50
    },
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
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = str(data.get("tamano", "5"))

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        # Llamada a GPT para análisis visual
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta cotizadora de uñas. Analiza la imagen y describe la forma, técnica, y decoraciones visibles por uña para cotizar según las siguientes reglas: forma, técnica base y decoraciones extra se suman. Si solo ves una mano, considera que es lo mismo para ambas."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe visualmente la forma, técnica y decoraciones visibles en esta imagen. Tamaño de uña: #{tamano}."},
                        {
                            "type": "image_url",
                            "image_url": {"url": imagen, "detail": "low"}
                        }
                    ]
                }
            ]
        )

        descripcion = response.choices[0].message.content.lower()
        total = 0
        desglose = []
        forma_detectada = None
        extras_detectados = {}

        # Tamaño
        precio_tamano = TABLAS["tamanos"].get(tamano, 0)
        total += precio_tamano
        desglose.append(f"Tamaño de uña #{tamano}: ${precio_tamano}")

        # Forma
        for forma, precio in TABLAS["formas"].items():
            if forma in descripcion:
                forma_detectada = forma
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        # Extras
        for extra, precio in TABLAS["extras"].items():
            if extra in descripcion:
                unidades = 10
                extras_detectados[extra] = unidades
                total += precio * unidades
                desglose.append(f"{extra.title()} x{unidades}: ${precio * unidades}")

        return jsonify({
            "descripcion": descripcion.strip(),
            "forma_detectada": forma_detectada,
            "extras_detectados": extras_detectados,
            "precio_tamano": precio_tamano,
            "resultado": "\n".join(desglose + [f"\nPrecio total estimado: ${round(total, 2)} MXN"])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
