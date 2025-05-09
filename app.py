
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
        tamano = int(data.get("tamano", 5))  # Default to 5 si no se proporciona

        if not imagen:
            return jsonify({"error": "Imagen no recibida"}), 400

        # Consultar a OpenAI con la imagen
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres una experta en uñas acrílicas. Recibirás una imagen y deberás identificar: forma, técnica, decoraciones o extras. Responde con esos elementos claramente descritos."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe forma, técnica y decoraciones que ves. Tamaño: {tamano}."},
                        {
                            "type": "image_url",
                            "image_url": { "url": imagen, "detail": "low" }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        descripcion = response.choices[0].message.content.lower()

        # Tablas de precio
        tecnicas = {
            "baño de acrílico": 230,
            "gel semipermanente": 60,
            "dipping": 200,
            "rubber": 60,
            "polygel": 60
        }

        formas = {
            "cuadrada": 0,
            "almendra": 50,
            "coffin": 50
        }

        tamanos = {
            1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
            6: 480, 7: 540, 8: 590, 9: 640, 10: 690
        }

        extras = {
            "tono extra": 25,
            "glitter": 20,
            "encapsulado": 30,
            "sticker": 30,
            "efecto en polvo": 15,
            "efecto espejo": 5,
            "foil": 5,
            "mano alzada sencilla": 10,
            "mano alzada compleja": 18,
            "3d": 15,
            "pedrería chica": 15,
            "pedrería grande": 30,
            "dije chico": 10,
            "dije grande": 20,
            "difuminados": 5,
            "french": 10,
            "ojo de gato": 5,
            "baby boomer": 15
        }

        total = tamanos.get(tamano, 440)
        detalle = [f"Tamaño uña #{tamano}: ${total}"]

        for tecnica, precio in tecnicas.items():
            if tecnica in descripcion:
                total += precio
                detalle.append(f"Técnica {tecnica}: ${precio}")

        for forma, precio in formas.items():
            if forma in descripcion:
                total += precio
                detalle.append(f"Forma {forma}: ${precio}")

        for extra, precio in extras.items():
            if extra in descripcion:
                total += precio
                detalle.append(f"Extra {extra}: ${precio}")

        resumen = "\n".join(detalle)
        final = f"{resumen}\n\nPrecio total estimado: ${total:.2f} MXN"

        return jsonify({"resultado": final})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
