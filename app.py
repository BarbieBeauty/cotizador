from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import base64
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")  # debes definir esta variable en tu entorno

def subir_a_imgbb(imagen_base64):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": imagen_base64
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        return None

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = data.get("tamano")

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        imagen_base64 = imagen.split(",")[1] if "," in imagen else imagen
        url_imagen = subir_a_imgbb(imagen_base64)

        if not url_imagen:
            return jsonify({"error": "No se pudo subir la imagen a ImgBB"}), 500

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta en uñas acrílicas. Analiza la imagen y cotiza con base en técnica, forma y decoraciones. No inventes precios, solo describe si no puedes calcular."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analiza esta imagen de uñas. El tamaño seleccionado es #" + str(tamano)},
                        {"type": "image_url", "image_url": {"url": url_imagen, "detail": "low"}}
                    ]
                }
            ]
        )

        return jsonify({"resultado": response.choices[0].message.content.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)