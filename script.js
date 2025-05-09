
async function cotizar() {
  const input = document.getElementById("imagen");
  const resultado = document.getElementById("resultado");
  const preview = document.getElementById("preview");
  const tamanio = document.getElementById("tamanio").value; // Tamaño de uña seleccionado

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
        let texto = data.resultado;

        // Extraer forma, técnica y extras
        const forma = /forma:\*\* (.+?)(\n|\*\*)/i.exec(texto)?.[1]?.trim().toLowerCase() || "";
        const tecnica = /t[ée]cnica:\*\* (.+?)(\n|\*\*)/i.exec(texto)?.[1]?.trim().toLowerCase() || "";
        const extras = texto.match(/- (.+?):? \$?[0-9]+/gi)?.map(e => e.replace(/^-\s*/, "").split(":")[0].trim().toLowerCase()) || [];

        // Precios de referencia
        const precios = {
          forma: { "cuadrada": 0, "almendra": 50, "coffin": 50 },
          tecnica: {
            "baño de acrilico": 230,
            "gel semipermanente": 60,
            "dipping": 200,
            "rubber": 60,
            "polygel": 60
          },
          extras: {
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
            "relieve": 15,
            "pedreria chica": 1.5,
            "pedreria grande": 30,
            "dije chico": 10,
            "dije grande": 20,
            "difuminados": 5,
            "french": 10,
            "ojo de gato": 5,
            "baby boomer": 15
          },
          tamanio: {
            "1": 260, "2": 280, "3": 330, "4": 380, "5": 440,
            "6": 480, "7": 540, "8": 590, "9": 640, "10": 690
          }
        };

        let total = 0;
        const f = Object.keys(precios.forma).find(key => forma.includes(key));
        if (f) total += precios.forma[f];

        const t = Object.keys(precios.tecnica).find(key => tecnica.includes(key));
        if (t) total += precios.tecnica[t];

        extras.forEach(extra => {
          if (precios.extras[extra]) total += precios.extras[extra];
        });

        const precioTamanio = precios.tamanio[tamanio] || 0;
        total += precioTamanio;

        resultado.innerHTML = `
          <div class="analisis">${data.resultado}</div>
          <div class="precio-final">
            <h3><span>✨</span> Precio total estimado:</h3>
            <p>$${total.toFixed(2)} MXN</p>
          </div>
          <a href="https://wa.me/526141170236?text=${encodeURIComponent(data.resultado + '\nPrecio estimado: $' + total.toFixed(2) + ' MXN')}" target="_blank">
            <button class="whatsapp">Enviar por WhatsApp</button>
          </a>`;
      } else {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
      }
    } catch (error) {
      console.error(error);
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
    }
  };
  reader.readAsDataURL(file);
}
