async function cotizar() {
  const input = document.getElementById("imagen");
  const resultado = document.getElementById("resultado");
  const preview = document.getElementById("preview");
  const tamanoInput = document.getElementById("tamano-uña");
  const tamanoUña = parseInt(tamanoInput.value);

  if (!input.files[0]) {
    resultado.innerHTML = "Por favor sube una imagen.";
    return;
  }

  const file = input.files[0];
  const reader = new FileReader();

  reader.onloadend = async () => {
    const imagenBase64 = reader.result;
    preview.innerHTML = `<img src="${imagenBase64}" />`;
    resultado.innerHTML = "⏳ Analizando imagen...";

    try {
      const res = await fetch("https://barbie-beauty-backend.onrender.com/analizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imagen: imagenBase64, token: "barbie1234" })
      });

      const data = await res.json();
      if (!data.resultado) {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
        return;
      }

      const texto = data.resultado;

      // --- Precios base ---
      const tecnicas = {
        "baño de acrílico": 230,
        "gel semipermanente": 60,
        "dipping": 200,
        "rubber": 60,
        "polygel": 60
      };

      const formas = {
        "cuadrada": 0,
        "almendra": 50,
        "coffin": 50
      };

      const extras = {
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
        "pedrería chica": 1.5 * 10,
        "pedrería grande": 30,
        "dije chico": 10,
        "dije grande": 20,
        "difuminados": 5,
        "french": 10,
        "ojo de gato": 5,
        "baby boomer": 15
      };

      const tamanos = {
        1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
        6: 480, 7: 540, 8: 590, 9: 640, 10: 690
      };

      let total = 0;

      const textoLower = texto.toLowerCase();

      // Técnica
      for (let clave in tecnicas) {
        if (textoLower.includes(clave)) {
          total += tecnicas[clave];
          break;
        }
      }

      // Forma
      for (let clave in formas) {
        if (textoLower.includes(clave)) {
          total += formas[clave];
          break;
        }
      }

      // Tamaño
      if (tamanos[tamanoUña]) {
        total = tamanos[tamanoUña];
      }

      // Extras
      for (let clave in extras) {
        if (textoLower.includes(clave)) {
          total += extras[clave];
        }
      }

      resultado.innerHTML = `
        <div style="text-align: left; white-space: pre-wrap; margin-bottom: 20px;">${texto}</div>
        <div style="background: #ffe6f0; padding: 15px; border: 2px dashed deeppink; border-radius: 12px; font-size: 20px;">
          ✨ <strong>Precio total estimado:</strong>
          <div style="color: #c2185b; font-size: 28px; font-weight: bold;">$${total.toFixed(2)} MXN</div>
        </div>
        <a href="https://wa.me/526141170236?text=${encodeURIComponent(data.resultado)}%0A%0APrecio estimado: $${total.toFixed(2)} MXN" target="_blank">
          <button style="margin-top: 15px; background: #25D366;">Enviar por WhatsApp</button>
        </a>
      `;
    } catch (error) {
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
      console.error(error);
    }
  };

  reader.readAsDataURL(file);
}

