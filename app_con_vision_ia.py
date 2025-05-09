
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import re

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
        tamano = int(data.get("tamano", 5))

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        # Paso 1: Análisis visual con GPT
        prompt = (
            "Analiza esta imagen de uñas. Menciona la forma (cuadrada, almendra o coffin), la técnica (acrílico, semipermanente, polygel, etc.), "
            "y todas las decoraciones visibles como french, babyboomer, pedrería, efecto dorado, mano alzada, etc. Sé específica y profesional. "
            "No inventes si no estás segura."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Eres una experta en uñas que analiza imágenes para cotizar con precisión." },
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": prompt },
                        { "type": "image_url", "image_url": { "url": imagen, "detail": "low" } }
                    ]
                }
            ],
            max_tokens=1000
        )

        descripcion = response.choices[0].message.content.strip().lower()

        # Paso 2: Calcular precio según las tablas reales
        total = 0
        desglose = []

        # Precios por técnica
        tecnicas_fijas = {
            "gel semipermanente": 60,
            "dipping": 200,
            "rubber": 60,
            "polygel": 60
        }

        precios_acrilico = {
            1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
            6: 480, 7: 540, 8: 590, 9: 640, 10: 690
        }

        if "acrílico" in descripcion or "acrilico" in descripcion:
            base = precios_acrilico.get(tamano, 440)
            total += base
            desglose.append(f"Técnica acrílico (#{tamano}): ${base}")
        else:
            for tecnica, precio in tecnicas_fijas.items():
                if tecnica in descripcion:
                    total += precio
                    desglose.append(f"Técnica {tecnica}: ${precio}")
                    break

        # Forma
        formas = {
            "almendra": 50,
            "coffin": 50,
            "cuadrada": 0
        }

        for forma, precio in formas.items():
            if forma in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        # Extras
        extras_precio = {
            "extra french": 10,
            "babyboomer": 15,
            "pedrería chica": 15,
            "pedrería grande": 30,
            "mano alzada sencilla": 10,
            "efecto dorado": 10,
            "3d": 15,
            "dije chico": 10,
            "dije grande": 20,
            "difuminados": 5,
            "tono extra": 25,
            "glitter": 20,
            "encapsulado": 30,
            "sticker": 30,
            "efecto en polvo": 15,
            "efecto espejo": 5,
            "foil": 5,
            "ojo de gato": 5,
            "mano alzada compleja": 18
        }

        for extra, precio in extras_precio.items():
            if extra in descripcion:
                total += precio
                desglose.append(f"Decoración {extra}: ${precio}")

        resumen = "\n".join(desglose)
        final = f"{resumen}\n\nPrecio total estimado: ${total:.2f} MXN"

        return jsonify({"resultado": final})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
