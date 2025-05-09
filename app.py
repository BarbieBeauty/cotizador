
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = data.get("tamano")
        if not imagen or not tamano:
            return jsonify({"error": "Imagen o tamaño no recibido"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta en uñas acrílicas. Recibirás una imagen base64 y un tamaño de uña, deberás analizar el diseño, forma, técnica y decoraciones por dedo, y calcular el precio total según las tablas proporcionadas para cada forma, técnica y extra por uña, multiplicando por dos manos."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analiza esta imagen y calcula el precio total considerando que el tamaño es #{tamano}."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": imagen,
                                "detail": "high"
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
