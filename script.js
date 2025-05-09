
async function cotizar() {
  const input = document.getElementById("imagen");
  const resultado = document.getElementById("resultado");
  const preview = document.getElementById("preview");
  const tamano = document.getElementById("tamano-uña").value;

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
        body: JSON.stringify({ imagen: imagenBase64, token: "barbie1234", tamano: tamano })
      });

      const data = await res.json();

      if (data.resultado) {
        const partes = data.resultado.split("Precio total estimado:");
        const detalles = partes[0].trim();
        const total = partes[1] ? partes[1].trim() : "No disponible";

        resultado.innerHTML = `
          <div>${detalles}</div>
          <div class="precio-final">✨ Precio total estimado: ${total}</div>
          <a href="https://wa.me/526141170236?text=${encodeURIComponent(data.resultado)}" target="_blank">
            <button style="margin-top: 15px; background: #25D366;">Enviar por WhatsApp</button>
          </a>
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
