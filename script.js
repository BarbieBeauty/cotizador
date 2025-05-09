async function cotizar() {
  const input = document.getElementById("imagen");
  const resultado = document.getElementById("resultado");
  const preview = document.getElementById("preview");

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
      console.log(data);

      if (data.resultado) {
        resultado.innerHTML = `
          <div class="cotizacion-contenedor">
            <h3>💅 Resultado del análisis:</h3>
            <pre>${data.resultado}</pre>
            <div class="precio-estimado">
              <p>✨ <strong>Precio total estimado:</strong></p>
              <p class="precio-final">${extraerPrecio(data.resultado)}</p>
            </div>
            <a href="https://wa.me/526141170236?text=${encodeURIComponent(data.resultado)}" target="_blank">
              <button class="btn-whatsapp">Enviar por WhatsApp</button>
            </a>
          </div>
        `;
      } else {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
      }
    } catch (error) {
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
    }
  };

  reader.readAsDataURL(file);
}

function extraerPrecio(texto) {
  const regex = /precio total estimado[:\s]*\$[\d,]+(?:\s*-\s*\$[\d,]+)?/i;
  const match = texto.match(regex);
  return match ? match[0].split(":")[1].trim() : "No disponible";
}

