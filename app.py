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
        prompt_base = (
            f"Eres una IA que analiza imágenes de uñas. "
            f"Tu tarea es detectar la forma de las uñas (almendra, cuadrada o coffin), "
            f"y contar cuántas uñas tienen cada una de las siguientes decoraciones: "
            f"french, baby boomer, pedrería chica, pedrería grande, glitter, efecto dorado, dijes, "
            f"corazones, mármol, ojo de gato, mano alzada sencilla, mano alzada compleja y 3d. "
            f"Devuelve una lista detallada con conteos exactos por decoración. Tamaño indicado: #{tamano}."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en analizar uñas a partir de imágenes."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_base},
                        {"type": "image_url", "image_url": {"url": imagen, "detail": "high"}}
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

        for forma in PRECIOS["formas"]:
            if forma in descripcion:
                precio_forma = PRECIOS["formas"][forma]
                total += precio_forma
                desglose.append(f"Forma {forma}: ${precio_forma}")
                break

        for extra, precio in PRECIOS["extras"].items():
            if extra in descripcion:
                import re
                match = re.search(rf"{extra} x?(\d+)", descripcion)
                cantidad = int(match.group(1)) if match else 1
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
