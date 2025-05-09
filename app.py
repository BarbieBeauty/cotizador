
from flask import Flask, request, jsonify
import openai
import os
import base64
from flask_cors import CORS

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

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        # limpiar base64
        image_data = imagen.split(",")[1] if "," in imagen else imagen
        image_bytes = base64.b64decode(image_data)

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres una experta en uñas acrílicas. Analiza la imagen y cotiza con base en técnica, forma y decoraciones. No inventes precios, solo describe si no puedes calcular."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analiza esta imagen de uñas. El tamaño seleccionado es #" + str(tamano)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}", "detail": "low"}}
                ]}
            ]
        )

        return jsonify({"resultado": response.choices[0].message.content.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
