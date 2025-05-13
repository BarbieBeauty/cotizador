import base64
import requests
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Coloca tu clave de API aquí
OPENAI_API_KEY = "tu_clave_api"

# Precios oficiales por etiqueta
PRECIOS = {
    "forma_almendra": 10,
    "forma_cuadrada": 5,
    "coffin": 8,
    "babyboomer": 30,
    "extra_french": 20,
    "pedreria_chica": 10,
    "efecto_dorado": 15,
    "marble": 25,
    "mano_alzada_sencilla": 18
}

def generar_prompt():
    return (
        "Analiza esta imagen de uñas y responde solo con una lista JSON con los elementos visibles. "
        "Las etiquetas válidas son: forma_almendra, forma_cuadrada, coffin, babyboomer, extra_french, "
        "pedreria_chica, efecto_dorado, marble, mano_alzada_sencilla. "
        "Incluye cada etiqueta tantas veces como aparezca (una por uña decorada). "
        "Ejemplo de respuesta válida: ['forma_cuadrada', 'extra_french', 'pedreria_chica', 'extra_french']."
    )

def analizar_imagen_con_openai(base64_image: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": generar_prompt()},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    result = response.json()
    try:
        content = result["choices"][0]["message"]["content"]
        etiquetas = eval(content)
        return etiquetas
    except Exception as e:
        print("Error en la respuesta:", result)
        return []

def calcular_cotizacion(etiquetas):
    desglose = {}
    total = 0
    for etiqueta in etiquetas:
        precio = PRECIOS.get(etiqueta, 0)
        desglose[etiqueta] = desglose.get(etiqueta, 0) + precio
        total += precio
    return {"total": total, "desglose": desglose}

@app.post("/cotizar")
async def cotizar_imagen(file: UploadFile = File(...)):
    image_bytes = await file.read()
    base64_img = base64.b64encode(image_bytes).decode("utf-8")

    etiquetas_detectadas = analizar_imagen_con_openai(base64_img)
    cotizacion = calcular_cotizacion(etiquetas_detectadas)

    return {
        "etiquetas_detectadas": etiquetas_detectadas,
        "cotizacion_total": cotizacion["total"],
        "desglose": cotizacion["desglose"]
    }
