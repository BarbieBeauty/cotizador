
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

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
        tamano = int(data.get("tamano", 5))  # Default a #5 si no se proporciona

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        # Pregunta para obtener solo etiquetas válidas
        prompt = (
            "Analiza la imagen de uñas y responde únicamente en formato JSON válido con estas etiquetas:

"
            "{\n"
            "  'tecnica': 'acrilico' | 'gel semipermanente' | 'dipping' | 'rubber' | 'polygel',
"
            "  'forma': 'forma_cuadrada' | 'forma_almendra' | 'forma_coffin',
"
            "  'extras': ['extra_french', 'babyboomer', 'pedreria_chica', 'pedreria_grande', 'mano_alzada_sencilla', 'efecto_dorado', '3d', ...]
"
            "}

"
            "No expliques nada. Solo responde con las etiquetas detectadas."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Eres una IA que etiqueta estilos de uñas para cotización precisa." },
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

        import json
        etiquetas = json.loads(response.choices[0].message.content.strip())

        tecnica = etiquetas.get("tecnica", "")
        forma = etiquetas.get("forma", "")
        extras = etiquetas.get("extras", [])

        # Precios
        precio_total = 0
        desglose = []

        # Técnicas base
        tecnicas_fijas = {
            "gel semipermanente": 60,
            "dipping": 200,
            "rubber": 60,
            "polygel": 60
        }

        # Acrílico por número
        precios_acrilico = {
            1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
            6: 480, 7: 540, 8: 590, 9: 640, 10: 690
        }

        if tecnica.lower() in ["acrilico", "acrílico"]:
            precio_base = precios_acrilico.get(tamano, 440)
            desglose.append(f"Técnica acrílico (# {tamano}): ${precio_base}")
        elif tecnica in tecnicas_fijas:
            precio_base = tecnicas_fijas[tecnica]
            desglose.append(f"Técnica {tecnica}: ${precio_base}")
        else:
            precio_base = 0
            desglose.append("Técnica no detectada")

        precio_total += precio_base

        # Forma
        formas = {
            "forma_cuadrada": 0,
            "forma_almendra": 50,
            "forma_coffin": 50
        }
        precio_forma = formas.get(forma, 0)
        if forma:
            desglose.append(f"Forma {forma.replace('_', ' ')}: ${precio_forma}")
        precio_total += precio_forma

        # Extras
        extras_precio = {
            "tono extra": 25,
            "glitter": 20,
            "encapsulado": 30,
            "sticker": 30,
            "efecto en polvo": 15,
            "efecto espejo": 5,
            "foil": 5,
            "mano_alzada_sencilla": 10,
            "mano_alzada_compleja": 18,
            "3d": 15,
            "pedreria_chica": 15,
            "pedreria_grande": 30,
            "dije_chico": 10,
            "dije_grande": 20,
            "difuminados": 5,
            "extra_french": 10,
            "ojo de gato": 5,
            "babyboomer": 15,
            "efecto_dorado": 10
        }

        for extra in extras:
            if extra in extras_precio:
                precio_total += extras_precio[extra]
                desglose.append(f"Extra {extra.replace('_', ' ')}: ${extras_precio[extra]}")

        resumen = "\n".join(desglose)
        final = f"{resumen}\n\nPrecio total estimado: ${precio_total:.2f} MXN"

        return jsonify({"resultado": final})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
