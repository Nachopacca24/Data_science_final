// Pantalla de recomendaciones: busca favoritos, pide la lista a la API y la muestra.
const MAX_FAVORITOS = 5;
const $ = (id) => document.getElementById(id);
const favoritos = new Map(); // appid -> nombre
const quetzales = (n) => `Q${n.toFixed(2)}`;

async function api(ruta, opciones) {
  const r = await fetch(ruta, opciones);
  const cuerpo = await r.json().catch(() => ({}));
  if (!r.ok) {
    const detalles = (cuerpo.detalles || []).map((d) => `${d.campo}: ${d.problema}`).join("; ");
    throw new Error(detalles || cuerpo.mensaje || `Error ${r.status}`);
  }
  return cuerpo;
}

function mostrarError(mensaje) {
  $("error").textContent = mensaje;
  $("error").hidden = !mensaje;
}

function pintarFavoritos() {
  const ul = $("favoritos");
  ul.replaceChildren(...[...favoritos].map(([appid, nombre]) => {
    const li = document.createElement("li");
    li.textContent = nombre;
    const quitar = document.createElement("button");
    quitar.type = "button";
    quitar.textContent = "×";
    quitar.setAttribute("aria-label", `Quitar ${nombre}`);
    quitar.onclick = () => { favoritos.delete(appid); pintarFavoritos(); };
    li.append(quitar);
    return li;
  }));
  $("buscar").disabled = favoritos.size >= MAX_FAVORITOS;
}

let espera;
$("buscar").addEventListener("input", (ev) => {
  clearTimeout(espera);
  const texto = ev.target.value.trim();
  const ul = $("sugerencias");
  if (texto.length < 2) { ul.hidden = true; return; }
  espera = setTimeout(async () => {
    try {
      const juegos = await api(`/juegos?buscar=${encodeURIComponent(texto)}&limite=8`);
      ul.replaceChildren(...juegos.filter((j) => !favoritos.has(j.appid)).map((j) => {
        const li = document.createElement("li");
        li.setAttribute("role", "option");
        li.tabIndex = 0;
        li.textContent = j.nombre;
        const elegir = () => {
          favoritos.set(j.appid, j.nombre);
          $("buscar").value = "";
          ul.hidden = true;
          pintarFavoritos();
          $("buscar").focus();
        };
        li.onclick = elegir;
        li.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); elegir(); } };
        return li;
      }));
      ul.hidden = ul.children.length === 0;
    } catch (e) { mostrarError(e.message); }
  }, 200);
});

function tarjeta(j) {
  const li = document.createElement("li");
  const img = document.createElement("img");
  img.src = j.imagen; img.alt = ""; img.loading = "lazy";
  const info = document.createElement("div");
  const nombre = document.createElement("strong");
  nombre.textContent = j.nombre;
  const datos = document.createElement("span");
  datos.textContent = `${Math.round(j.p_bien_recibido * 100)} % de que sea bien recibido · parecido ${Math.round(j.similitud * 100)} %`;
  info.append(nombre, datos);
  const precio = document.createElement("span");
  precio.className = "precio";
  precio.textContent = quetzales(j.precio_gtq);
  li.append(img, info, precio);
  return li;
}

$("formulario").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  mostrarError("");
  $("resultado").hidden = true; // nunca mostrar una lista vieja junto a un error
  const presupuesto = Number($("presupuesto").value);
  if (favoritos.size === 0) return mostrarError("Elige al menos un juego que te haya gustado.");
  if (!(presupuesto > 0)) return mostrarError("El presupuesto debe ser mayor que cero.");

  $("enviar").disabled = true;
  try {
    const r = await api("/recomendaciones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ presupuesto, favoritos: [...favoritos.keys()] }),
    });
    $("r-presupuesto").textContent = quetzales(r.presupuesto);
    $("lista").replaceChildren(...r.juegos.map(tarjeta));
    $("vacia").hidden = r.juegos.length > 0;
    $("r-total").textContent = quetzales(r.total_gtq);
    $("r-restante").textContent = quetzales(r.restante_gtq);
    $("resultado").hidden = true; // CAMBIO INTENCIONAL PARA LA DEMOSTRACIÓN E2E
  } catch (e) {
    mostrarError(e.message);
  } finally {
    $("enviar").disabled = false;
  }
});

$("max-favoritos").textContent = MAX_FAVORITOS;
api("/version").then((v) => { $("version").textContent = `versión ${v.version.slice(0, 7)} · ${v.ambiente}`; }).catch(() => {});
