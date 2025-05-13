from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import re

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
        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
  "role": "system",
  "content": (
    "Eres un experto en análisis de uñas con experiencia en cotizaciones de salones de belleza. "
    "Tu tarea es detectar con precisión los siguientes elementos en la imagen:\n\n"
    "1. **Forma de las uñas** (almendra, cuadrada, coffin)\n"
    "2. **Decoraciones o efectos por uña** incluyendo:\n"
    "- Pedrería (chica o grande)\n"
    "- Glitter o efecto escarchado\n"
    "- Mármol\n"
    "- Efecto dorado\n"
    "- French clásico o invertido\n"
    "- Baby boomer\n"
    "- Mano alzada (sencilla o compleja)\n"
    "- Diseños 3D\n"
    "- Corazones u otros adornos visibles\n"
    "- Ojo de gato\n\n"
    "Cuenta cuántas uñas tienen cada uno de estos efectos.\n"
    "No inventes decoraciones si no son claramente visibles en la imagen.\n"
    "Responde de forma directa, clara y en español, especificando cantidades detectadas por tipo."
  )
}

                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe visualmente esta imagen. Tamaño de uña: #{tamano}."},
                        {"type": "image_url", "image_url": {"url": imagen, "detail": "low"}}
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

        # Detectar forma
        for forma, precio in PRECIOS["formas"].items():
            if forma in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        # Detectar decoraciones con cantidades
        for extra, precio in PRECIOS["extras"].items():
            patrones = [
                rf"{extra}.*?(\d+)",
                rf"{extra}.*?x\s?(\d+)",
                rf"{extra}.*?(\d+)\s*uñas?",
            ]
            cantidad_detectada = 0
            for patron in patrones:
                match = re.search(patron, descripcion)
                if match:
                    cantidad_detectada = int(match.group(1))
                    break

            if cantidad_detectada > 0:
                subtotal = precio * cantidad_detectada
                total += subtotal
                desglose.append(f"{extra.capitalize()} x{cantidad_detectada}: ${subtotal}")

        desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

        return jsonify({
            "descripcion": descripcion,
            "resultado": "\n".join(desglose)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
