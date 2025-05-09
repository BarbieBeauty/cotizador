from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

PRECIOS = {
    "forma_cuadrada": 0,
    "forma_almendra": 50,
    "forma_coffin": 50,
    "babyboomer": 15,
    "pedreria_chica": 1.5,
    "extra_french": 10,
    "efecto_dorado": 5,
    "mano_alzada_sencilla": 10,
}

TAMANOS = {
    "1": 260, "2": 280, "3": 330, "4": 380, "5": 440,
    "6": 480, "7": 540, "8": 590, "9": 640, "10": 690
}

@app.route("/analizar", methods=["POST"])
def analizar():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 401

    imagen = data.get("imagen")
    tamano = str(data.get("tamano", "1"))

    if not imagen:
        return jsonify({"error": "Imagen no recibida"}), 400

    prompt = '''
Eres una experta en uñas. Analiza la imagen enviada y devuélveme una lista en formato JSON con las características que observes, usando exactamente estas etiquetas si aplican:
- forma_cuadrada, forma_almendra, forma_coffin
- babyboomer, pedreria_chica, extra_french, efecto_dorado, mano_alzada_sencilla

Ejemplo:
["forma_almendra", "babyboomer", "efecto_dorado", "pedreria_chica", "pedreria_chica"]
'''

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Aquí está la imagen para analizar:"},
                    {"type": "image_url", "image_url": {"url": imagen, "detail": "low"}}
                ]}
            ],
            max_tokens=500
        )

        etiquetas = eval(response.choices[0].message.content.strip())
        resumen = {}
        total = 0

        if tamano in TAMANOS:
            resumen[f"Tamaño de uña #{tamano}"] = TAMANOS[tamano]
            total += TAMANOS[tamano]

        for etiqueta in etiquetas:
            precio = PRECIOS.get(etiqueta, 0)
            resumen[etiqueta] = resumen.get(etiqueta, 0) + precio
            total += precio

        return jsonify({
            "resumen": resumen,
            "total": total
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
