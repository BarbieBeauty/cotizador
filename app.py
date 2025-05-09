from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
SECRET_TOKEN = "barbie1234"

# Precios de referencia extraídos de tus tablas
PRECIOS = {
    "formas": {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50,
    },
    "tamano": {
        "1": 260, "2": 280, "3": 330, "4": 380, "5": 440,
        "6": 480, "7": 540, "8": 590, "9": 640, "10": 690
    },
    "extras_por_uña": {
        "babyboomer": 15,
        "french": 10,
        "pedreria chica": 1.5,
        "pedreria grande": 30,
        "glitter": 20,
        "efecto dorado": 5,
        "efecto espejo": 5,
        "tono extra": 25,
        "dije chico": 10,
        "dije grande": 20,
        "difuminados": 5,
        "ojo de gato": 5,
        "mano alzada sencilla": 10,
        "mano alzada compleja": 18,
        "encapsulado": 30,
        "sticker": 30,
        "3d": 15,
    }
}

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        data = request.get_json()

        if data.get("token") != SECRET_TOKEN:
            return jsonify({"error": "Token inválido"}), 401

        imagen = data.get("imagen")
        tamano = str(data.get("tamano_uña", "1"))

        if not imagen or not imagen.startswith("data:image"):
            return jsonify({"error": "Imagen inválida o no recibida"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres una experta en uñas. Recibirás una imagen base64 y deberás analizar su forma, técnica y decoración. "
                        "Después responde únicamente con lo siguiente en formato JSON:\n"
                        "{\n"
                        "  'forma': 'almendra' | 'cuadrada' | 'coffin',\n"
                        "  'extras': ['babyboomer', 'glitter', ...] usando sólo los nombres de la lista de precios,\n"
                        "  'cantidad_extras': {'nombre_extra': numero_de_uñas_afectadas},\n"
                        "  'comentario': 'descripción del diseño'\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analiza la imagen y devuelve el JSON con forma, extras, cantidades y comentario."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": imagen,
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        resultado_texto = response.choices[0].message.content

        import json, re
        match = re.search(r"\{.*\}", resultado_texto, re.DOTALL)
        if not match:
            return jsonify({"resultado": "No se pudo interpretar la respuesta de la IA."})

        result_data = json.loads(match.group().replace("'", '"'))

        precio = 0
        detalles = []

        # Tamaño
        precio += PRECIOS["tamano"].get(tamano, 0)
        detalles.append(f"Tamaño de uña #{tamano}: ${PRECIOS['tamano'].get(tamano, 0)}")

        # Forma
        forma = result_data.get("forma", "").lower()
        precio += PRECIOS["formas"].get(forma, 0)
        detalles.append(f"Forma {forma}: ${PRECIOS['formas'].get(forma, 0)}")

        # Extras
        cantidad_extras = result_data.get("cantidad_extras", {})
        for extra, cantidad in cantidad_extras.items():
            extra_lower = extra.lower()
            if extra_lower in PRECIOS["extras_por_uña"]:
                total = PRECIOS["extras_por_uña"][extra_lower] * int(cantidad)
                precio += total
                detalles.append(f"{extra} (x{cantidad}): ${total}")

        texto_final = "<br>".join(detalles)
        texto_final += f"<br><br><strong>💅 Precio total estimado: ${precio:.2f} MXN</strong>"

        return jsonify({"resultado": texto_final, "comentario": result_data.get("comentario", "")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
