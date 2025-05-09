
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import base64

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
        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta en uñas acrílicas. Recibirás una imagen base64, deberás analizar el diseño, forma, técnica y decoraciones para cotizar en pesos mexicanos."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analiza esta imagen de uñas y dame la forma, técnica y decoraciones con precio en MXN."},
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
