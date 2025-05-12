
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

TABLAS = {
    "formas": {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50
    },
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
    try:
        data = request.get_json()
        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = str(data.get("tamano", "5"))

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta cotizadora de uñas. Analiza la imagen y describe la forma, técnica y decoraciones visibles por uña para cotizar según las siguientes reglas: forma, técnica base y decoraciones extra se suman. Si solo ves una mano, considera que es lo mismo para ambas."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe visualmente la forma, técnica y decoraciones visibles en esta imagen. Tamaño de uña: #{tamano}."},
                        {
                            "type": "image_url",
                            "image_url": {"url": imagen, "detail": "low"}
                        }
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

        for forma, precio in TABLAS["formas"].items():
            if forma in descripcion:
                total += precio
                desglose.append(f"Forma {forma}: ${precio}")
                break

        decoraciones_detectadas = []
        for extra, precio in TABLAS["extras"].items():
            match = False

            if extra == "efecto dorado":
    frases_dorado_completo = [
        "gran parte de la uña dorada", "recubrimiento dorado", "diseño dorado principal",
        "dorado dominante", "cubierta dorada", "dorado en casi toda la uña",
        "mayoría de la superficie dorada", "efecto dorado visible en toda la uña"
    ]
    exclusiones_plateado = ["plateado", "metálico plateado", "brillo plateado", "efecto espejo plateado"]
    if any(x in descripcion for x in exclusiones_plateado):
        continue
    if any(p in descripcion for p in frases_dorado_completo):
        match = True
    else:
        continue

                palabras_clave_dorado = [
                    "foil", "metálico", "brillante", "efecto dorado",
                    "dorado metálico", "foil dorado", "reflejo dorado", "brillo oro",
                    "acabado brillante", "líneas metálicas", "efecto espejo", "decoración dorada"
                ]
                if any(p in descripcion for p in palabras_clave_dorado):
                    match = True

            elif extra == "mármol":
                if "mármol" in descripcion and not any(p in descripcion for p in ["efecto dorado", "foil dorado", "dorado metálico", "brillo dorado"]):
                    match = True

            elif extra == "mano alzada sencilla":
                if any(p in descripcion for p in [
                    "mano alzada", "líneas artísticas", "trazos cruzados", "líneas en zigzag", "líneas diagonales", "trazos contrastantes", "triángulos decorativos", "figuras abstractas", "diseño gráfico",
                    "patrón geométrico", "diseño a mano", "diseño simétrico", "líneas blancas", "figuras decorativas"
                ]):
                    match = True

            elif extra in descripcion:
                match = True

            if match:
                unidades = 10
                total += precio * unidades
                decoraciones_detectadas.append(f"{extra.title()} x{unidades}: ${precio * unidades}")

        desglose.extend(decoraciones_detectadas)

        return jsonify({
            "descripcion": descripcion.strip(),
            "resultado": "\n".join(desglose + [f"\nPrecio total estimado: ${round(total, 2)} MXN"])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
