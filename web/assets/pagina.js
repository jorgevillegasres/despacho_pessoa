// Rellena los enlaces locales y las fichas de los agentes desde assets/datos.js.
(function () {
  const D = window.DESPACHO;
  document.querySelectorAll("[data-enlace]").forEach((a) => {
    const destino = a.dataset.enlace;
    if (!destino || destino === "zip" || destino === "repo") {
      a.removeAttribute("href");
      return;
    }
    a.href = "../" + destino;
  });

  const lista = document.getElementById("pestanas");
  const panel = document.getElementById("ficha");
  if (!lista || !panel) return;

  function fila(dl, titulo, valores, comoCodigo) {
    const dt = document.createElement("dt");
    dt.textContent = titulo;
    const dd = document.createElement("dd");
    valores.forEach((v, k) => {
      if (k) dd.append(", ");
      if (comoCodigo) {
        const c = document.createElement("code");
        c.textContent = v;
        dd.append(c);
      } else {
        dd.append(v);
      }
    });
    dl.append(dt, dd);
  }

  function mostrar(i) {
    [...lista.children].forEach((b, j) => {
      b.setAttribute("aria-selected", String(i === j));
      b.tabIndex = i === j ? 0 : -1;
    });
    const a = D.agentes[i];
    const h = document.createElement("h3");
    h.textContent = `${a.id.slice(0, 2)} · ${a.nombre} (${a.heteronimo})`;
    const cita = document.createElement("blockquote");
    cita.textContent = a.cita;
    // Search (02) escribió en inglés; los demás heterónimos, en portugués.
    cita.lang = a.id.startsWith("02-") ? "en" : "pt";
    const oficio = document.createElement("p");
    oficio.textContent = a.descripcion;
    const dl = document.createElement("dl");
    fila(dl, "Lee", a.lee, true);
    fila(dl, "Escribe", a.escribe, true);
    if (a.ejecuta.length) fila(dl, "Puede ejecutar", a.ejecuta, true);
    else fila(dl, "Puede ejecutar", ["ningún programa"], false);
    fila(dl, "Cómo falla", [a.falla], false);
    panel.replaceChildren(h, cita, oficio, dl);
    panel.setAttribute("aria-labelledby", lista.children[i].id);
  }

  D.agentes.forEach((a, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.id = "pestana-" + a.id;
    b.setAttribute("role", "tab");
    b.setAttribute("aria-controls", "ficha");
    b.textContent = a.heteronimo;
    b.addEventListener("click", () => mostrar(i));
    b.addEventListener("keydown", (ev) => {
      const n = D.agentes.length;
      let j;
      if (ev.key === "ArrowRight") j = (i + 1) % n;
      else if (ev.key === "ArrowLeft") j = (i - 1 + n) % n;
      else if (ev.key === "Home") j = 0;
      else if (ev.key === "End") j = n - 1;
      else return;
      ev.preventDefault();
      mostrar(j);
      lista.children[j].focus();
    });
    lista.append(b);
  });
  mostrar(0);
})();
