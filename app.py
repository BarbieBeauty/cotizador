from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import uuid
import json

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
                {"role": "system", "content": "Eres un asistente que analiza uñas. Describe detalladamente la forma, técnica base y cuántas uñas tienen cada tipo de decoración. Usa este formato: forma: coffin, glitter x4, pedrería chica x1, mármol x2..."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analiza esta imagen y cuenta decoraciones visibles. Tamaño de uña: #{tamano}."},
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
            if f"forma: {forma}" in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        for extra, precio_unitario in PRECIOS["extras"].items():
            for palabra in descripcion.split(","):
                if extra in palabra:
                    palabras = palabra.strip().split()
                    try:
                        cantidad = int(palabras[-1].replace("x", ""))
                        total += precio_unitario * cantidad
                        desglose.append(f"{extra.capitalize()} x{cantidad}: ${precio_unitario * cantidad}")
                    except:
                        continue

        guardar_historial(imagen, tamano, descripcion, desglose, total)

        desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")
        return jsonify({
            "descripcion": descripcion,
            "resultado": "\n".join(desglose)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def guardar_historial(imagen, tamano, descripcion, desglose, total):
    entry = {
        "id": str(uuid.uuid4()),
        "tamano": tamano,
        "descripcion": descripcion,
        "detalles": desglose,
        "total": round(total, 2),
        "imagen": imagen
    }
    historial_path = "historial.json"
    if os.path.exists(historial_path):
        with open(historial_path, "r") as f:
            historial = json.load(f)
    else:
        historial = []

    historial.append(entry)
    with open(historial_path, "w") as f:
        json.dump(historial, f, indent=2)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
