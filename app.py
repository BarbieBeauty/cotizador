from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

PRECIOS = {
    "forma": {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50
    },
    "efectos": {
        "babyboomer": 15,
        "french": 10,
        "pedreria_chica": 1.5,
        "pedreria_grande": 30,
        "mano_alzada_sencilla": 10,
        "mano_alzada_compleja": 18,
        "3d": 15,
        "corazon": 5
    }
}

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = int(data.get("tamano_uña", 1))
        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta en uñas acrílicas. Recibirás una imagen base64 de uñas, y debes identificar: forma, técnica y decoraciones como french, babyboomer, pedrería, etc. para cotizar."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe la forma, técnica y decoraciones visibles por uña para cotizar. Cuenta cuántas uñas tienen decoraciones distintas."},
                        {
                            "type": "image_url",
                            "image_url": {"url": imagen, "detail": "low"}
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        content = response.choices[0].message.content.lower()

        total = 0
        detalles = []

        # Tamaño base
        precios_tamano = {
            1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
            6: 480, 7: 540, 8: 590, 9: 640, 10: 690
        }
        base = precios_tamano.get(tamano, 260)
        total += base * 2  # considerar ambas manos
        detalles.append(f"Tamaño uña #{tamano}: ${base * 2}")

        # Forma
        for forma, precio in PRECIOS["forma"].items():
            if forma in content:
                total += precio
                detalles.append(f"Forma {forma}: ${precio}")
                break

        # Efectos
        for efecto, precio in PRECIOS["efectos"].items():
            if efecto in content:
                if "una uña" in content or "1 uña" in content:
                    cantidad = 1
                elif "dos uñas" in content or "2 uñas" in content:
                    cantidad = 2
                else:
                    cantidad = 10
                total += precio * cantidad
                detalles.append(f"{efecto.replace('_', ' ').capitalize()} x{cantidad}: ${precio * cantidad}")

        return jsonify({
            "detalles": detalles,
            "total": round(total, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)