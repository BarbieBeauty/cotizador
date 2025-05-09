async function cotizar() {
  const input = document.getElementById("imagen");
  const tamano = document.getElementById("tamano").value;
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
    preview.innerHTML = `<img src="${imagenBase64}" style="max-width:200px" />`;

    resultado.innerHTML = "⏳ Analizando imagen...";

    try {
      const res = await fetch("https://barbie-beauty-backend.onrender.com/analizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imagen: imagenBase64, token: "barbie1234", tamano: tamano })
      });

      const data = await res.json();

      if (data.resumen) {
        let html = "<ul>";
        for (let [clave, valor] of Object.entries(data.resumen)) {
          html += `<li>${clave}: $${valor}</li>`;
        }
        html += `</ul><h2>Total estimado: $${data.total.toFixed(2)} MXN</h2>`;
        resultado.innerHTML = html;
      } else {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
      }
    } catch (error) {
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
    }
  };
  reader.readAsDataURL(file);
}
