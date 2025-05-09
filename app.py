
from flask import Flask, request, jsonify
import openai
import os
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS

# Inicializar app
app = Flask(__name__)
CORS(app)  # permitir llamadas desde GitHub Pages

# Leer clave de OpenAI desde variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()
        imagen_b64 = data.get("imagen")
        token = data.get("token")

        if token != os.getenv("ACCESS_TOKEN"):
            return jsonify({"error": "Token inválido"}), 403

        if not imagen_b64:
            return jsonify({"error": "Imagen no recibida"}), 400

        image_bytes = base64.b64decode(imagen_b64.split(",")[-1])

        buffer = BytesIO(image_bytes)
        img = Image.open(buffer)
        buffer2 = BytesIO()
        img.save(buffer2, format="JPEG")
        img_data = base64.b64encode(buffer2.getvalue()).decode("utf-8")

        prompt = (
            "Analiza esta imagen de uñas. Indica: "
            "1) Forma (almendra, cuadrada, etc), "
            "2) Técnica (acrílico, babyboomer…), "
            "3) Decoraciones (pedrería, french, efecto dorado…), "
            "4) Calcula un precio estimado con base en: "
            "Acrílico $540, Almendra $50, Babyboomer $15, French $5, Pedrería chica $1.5 por pieza. "
            "Dame un desglose y total final."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
                    ]
                }
            ],
            max_tokens=800
        )

        result = response.choices[0].message.content
        return jsonify({"resultado": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
