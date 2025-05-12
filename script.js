
async function cotizar() {
  const input = document.getElementById("imagen");
  const resultado = document.getElementById("resultado");
  const preview = document.getElementById("preview");
  const tamano = document.getElementById("tamano").value;

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
        body: JSON.stringify({ imagen: imagenBase64, token: "barbie1234", tamano: parseInt(tamano) })
      });

      const data = await res.json();
      if (data.resultado) {
        resultado.innerHTML = `<pre>${data.resultado}</pre>`;
      } else {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
      }
    } catch (error) {
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
    }
  };
  reader.readAsDataURL(file);
}

document.getElementById("whatsappBtn").addEventListener("click", () => {
  const resultado = document.getElementById("resultado").innerText;
  const mensaje = `Hola! 💅%0A%0AQuiero cotizar este diseño de uñas:%0A%0A${encodeURIComponent(resultado)}%0A📸 Imagen cargada incluida en el sistema.`;
  window.open(`https://wa.me/526141170236?text=${mensaje}`, "_blank");
});
