
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

# Tablas de precios insertadas directamente
tablas_precios = """
TABLA DE PRECIOS:

TÉCNICAS BASE:
- BAÑO DE ACRÍLICO: $230
- GEL SEMIPERMANENTE: $60
- DIPPING: $200
- RUBBER: $60
- POLYGEL: $60

FORMAS:
- CUADRADA: $0
- ALMENDRA: $50
- COFFIN: $50

DECORACIONES EXTRA (precio por uña):
- TONO EXTRA: $25
- GLITTER: $20
- EFECTO MÁRMOL: $15
- EFECTO DORADO / FOIL: $15
- MANO ALZADA SENCILLA: $10
- MANO ALZADA COMPLEJA: $18
- FRENCH: $10
- PEDRERÍA CHICA (1.5 c/u): $1.5 por uña

TAMAÑO (Acrílico):
- ACRÍLICO #1: $260
- ACRÍLICO #2: $280
- ACRÍLICO #3: $330
- ACRÍLICO #4: $380
- ACRÍLICO #5: $440
- ACRÍLICO #6: $480
- ACRÍLICO #7: $540
- ACRÍLICO #8: $590
- ACRÍLICO #9: $640
- ACRÍLICO #10: $690
"""

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"Eres una experta cotizadora de uñas. Usa las siguientes tablas para dar una cotización precisa en MXN. Analiza cuidadosamente la forma, técnica, decoraciones y cantidad de uñas con base en la imagen. {tablas_precios}"
                },
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "Analiza esta imagen de uñas y genera la cotización completa con base en las tablas. Incluye forma, técnica, decoraciones por uña y precio total." },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": imagen,
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        return jsonify({"resultado": response.choices[0].message.content.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
