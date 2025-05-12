

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Configuración
openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

# Tablas de precios
TABLAS = {
    "formas": {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50
    },
    "tamanos": {
        str(i): p for i, p in zip(range(1, 11), [260, 280, 330, 380, 440, 480, 540, 590, 640, 690])
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

# Palabras clave para detección visual
PALABRAS_CLAVE = {
    "efecto_dorado": [
        "efecto dorado dominante", "gran parte de la uña dorada", "recubrimiento dorado",
        "dorado visible en casi toda la superficie", "cubierta dorada"
    ],
    "exclusiones_dorados": ["plateado", "plata", "cromo", "espejo", "metálico", "efecto espejo", "brillo plateado"],
    "mano_alzada_sencilla": [
        "mano alzada", "líneas artísticas", "trazos cruzados", "patrón geométrico", "diseño a mano", 
        "diseño simétrico", "líneas blancas", "figuras decorativas", "líneas diagonales", 
        "líneas en zigzag", "diseño gráfico", "triángulos decorativos", "trazos contrastantes", 
        "letras", "diseño personalizado", "dibujos"
    ],
    "mano_alzada_compleja": [
        "animal print", "efecto carey", "efecto tortoise", "efecto jaspeado",
        "manchas marrones", "efecto manchado", "estilo carey"
    ],
    "sinonimos_formas": {
        "almendra": ["almendra", "almendrada", "punta redonda", "forma ovalada", "curvatura suave"],
        "cuadrada": ["cuadrada", "punta recta", "forma recta"],
        "coffin": ["coffin", "bailarina"]
    }
}

def detectar_forma(descripcion):
    for forma, palabras in PALABRAS_CLAVE["sinonimos_formas"].items():
        if any(p in descripcion for p in palabras):
            return forma, TABLAS["formas"][forma]
    return None, 0

def detectar_decoraciones(descripcion):
    extras = []
    total = 0
    decoracion_activada = set()

    if any(p in descripcion for p in PALABRAS_CLAVE["efecto_dorado"]):
        if not any(e in descripcion for e in PALABRAS_CLAVE["exclusiones_dorados"]):
            extras.append(("Efecto Dorado", TABLAS["extras"]["efecto dorado"] * 10))
            total += TABLAS["extras"]["efecto dorado"] * 10
            decoracion_activada.add("efecto dorado")

    if any(p in descripcion for p in PALABRAS_CLAVE["mano_alzada_compleja"]):
        extras.append(("Mano Alzada Compleja", TABLAS["extras"]["mano alzada compleja"] * 10))
        total += TABLAS["extras"]["mano alzada compleja"] * 10
        decoracion_activada.add("mano alzada compleja")

    if "mano alzada compleja" not in decoracion_activada and any(p in descripcion for p in PALABRAS_CLAVE["mano_alzada_compleja"]):
        extras.append(("Mano Alzada Sencilla", TABLAS["extras"]["mano alzada sencilla"] * 10))
        total += TABLAS["extras"]["mano alzada sencilla"] * 10

    if any(p in descripcion for p in PALABRAS_CLAVE["mano_alzada_sencilla"]):
        extras.append(("Mano Alzada Sencilla", TABLAS["extras"]["mano alzada sencilla"] * 10))
        total += TABLAS["extras"]["mano alzada sencilla"] * 10

    return extras, total

@app.route("/analizar", methods=["POST"])
def analizar():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 401

    imagen = data.get("imagen")
    tamano = str(data.get("tamano", "5"))
    if not imagen:
        return jsonify({"error": "Imagen no recibida"}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "Describe la forma, técnica y decoraciones visibles en las uñas."},
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

        precio_tamano = TABLAS["tamanos"].get(tamano, 0)
        total += precio_tamano
        desglose.append(f"Tamaño de uña #{tamano}: ${precio_tamano}")

        forma_detectada, precio_forma = detectar_forma(descripcion)
        if forma_detectada:
            total += precio_forma
            desglose.append(f"Forma {forma_detectada}: ${precio_forma}")

        extras, total_extras = detectar_decoraciones(descripcion)
        total += total_extras
        for nombre, precio in extras:
            desglose.append(f"{nombre} x10: ${precio}")

        desglose.append(f"\nPrecio total estimado: ${round(total, 2)} MXN")

        return jsonify({
            "descripcion": descripcion,
            "resultado": "\n".join(desglose)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
