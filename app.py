from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
from datetime import datetime

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

FEEDBACK_PATH = "feedback.json"

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
        prompt = (
            f"Analiza detalladamente la imagen de estas uñas. Tamaño de uña: #{tamano}. "
            "Identifica con precisión: forma (almendra, cuadrada, coffin), y por cada uña decorada, menciona cada técnica o decoración visible: "
            "french, baby boomer, pedrería chica, pedrería grande, glitter, efecto dorado, corazones, mármol, ojo de gato, mano alzada sencilla, mano alzada compleja, 3d. "
            "Cuenta cuántas uñas tienen cada efecto y descríbelo de forma clara para poder calcular el precio correctamente."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en analizar diseños de uñas para cotizaciones."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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

        for forma, precio in PRECIOS["formas"].items():
            if forma in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        for extra, precio in PRECIOS["extras"].items():
            if extra in descripcion:
                cantidad = descripcion.count(extra)
                subtotal = precio * cantidad
                total += subtotal
                desglose.append(f"{extra.capitalize()} x{cantidad}: ${round(subtotal, 2)}")

        resultado = "\n".join(desglose + [f"\nPrecio total estimado: ${round(total, 2)} MXN"])

        # Guardar feedback para mejorar la lógica
        feedback_entry = {
            "fecha": datetime.now().isoformat(),
            "imagen": imagen,
            "descripcion": descripcion,
            "etiquetas_detectadas": desglose,
            "total_estimado": total
        }

        try:
            with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
                feedback_data = json.load(f)
        except FileNotFoundError:
            feedback_data = []

        feedback_data.append(feedback_entry)

        with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            "descripcion": descripcion,
            "resultado": resultado
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

