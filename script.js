
let datosAnalisis = null;

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
        datosAnalisis = data;
        mostrarResultado(data, tamano);
      } else {
        resultado.innerHTML = "❌ No se pudo procesar la imagen.";
      }
    } catch (error) {
      resultado.innerHTML = "❌ Error de conexión o del servidor.";
    }
  };
  reader.readAsDataURL(file);
}

document.getElementById("tamano").addEventListener("change", () => {
  if (datosAnalisis) {
    const nuevoTamano = parseInt(document.getElementById("tamano").value);
    mostrarResultado(datosAnalisis, nuevoTamano);
  }
});

function mostrarResultado(data, tamano) {
  let total = 0;
  const desglose = [];

  const precioTamano = {
    1: 260, 2: 280, 3: 330, 4: 380, 5: 440,
    6: 480, 7: 540, 8: 590, 9: 640, 10: 690
  }[tamano] || 0;

  total += precioTamano;
  desglose.push(`Tamaño de uña #${tamano}: $${precioTamano}`);

  if (data.forma_detectada) {
    const precioForma = {
      "cuadrada": 0,
      "almendra": 50,
      "coffin": 50
    }[data.forma_detectada] || 0;
    total += precioForma;
    desglose.push(`Forma ${data.forma_detectada}: $${precioForma}`);
  }

  for (let extra in data.extras_detectados) {
    const cantidad = data.extras_detectados[extra];
    const precio = {
      "french": 10,
      "baby boomer": 15,
      "pedrería chica": 1.5,
      "pedrería grande": 30,
      "glitter": 20,
      "efecto dorado": 15,
      "corazones": 10,
      "mármol": 15,
      "ojo de gato": 5,
      "mano alzada sencilla": 10,
      "mano alzada compleja": 18,
      "3d": 15
    }[extra] || 0;
    total += precio * cantidad;
    desglose.push(`${extra} x${cantidad}: $${(precio * cantidad).toFixed(2)}`);
  }

  document.getElementById("resultado").innerHTML =
    `<pre>${desglose.join("\n")}

Precio total estimado: $${total.toFixed(2)} MXN</pre>`;
}
