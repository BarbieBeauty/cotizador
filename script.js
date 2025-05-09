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
        body: JSON.stringify({ imagen: imagenBase64, token: "barbie1234", tamano_uña: tamano })
      });

      const data = await res.json();

      if (data.resultado) {
        resultado.innerHTML = `
          ${data.resultado}
          <br><br>
          <i style="color: #666;">${data.comentario || ''}</i>
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
