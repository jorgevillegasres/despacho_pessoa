// Presentación web del Despacho Pessoa: navegación, carril, aparición y pequeños movimientos.
// Sin dependencias. Si JavaScript falla, la página sigue siendo legible de arriba abajo.
(function () {
  "use strict";

  const html = document.documentElement;
  const body = document.body;
  const slides = [...document.querySelectorAll("section.slide")];
  const REPO = html.dataset.repo || "";

  // Enlaces al repositorio: data-repo="ruta/dentro/del/repo" o vacío para la raíz.
  document.querySelectorAll("[data-repo]").forEach((a) => {
    if (a === html) return;
    const ruta = a.dataset.repo;
    if (!REPO) { a.removeAttribute("href"); return; }
    a.href = ruta ? REPO.replace(/\/$/, "") + "/blob/main/" + ruta : REPO;
    a.target = "_blank";
    a.rel = "noopener";
  });
  document.querySelectorAll("[data-repo-text]").forEach((el) => {
    if (REPO) el.textContent = REPO.replace(/^https?:\/\//, "");
  });

  // Barra superior: se esconde al bajar o al cerrarla.
  const onScroll = () => body.classList.toggle("scrolled", window.scrollY > 40);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  const x = document.querySelector(".topbar .x");
  if (x) x.addEventListener("click", () => body.classList.add("bar-closed"));

  // Numeración de cada sección.
  slides.forEach((s, i) => {
    const num = s.querySelector(".kicker .num");
    if (num) num.textContent = String(i + 1).padStart(2, "0") + " / " + String(slides.length).padStart(2, "0");
  });

  // Carril derecho: un punto por sección, etiqueta con la parte actual.
  const rail = document.querySelector(".rail");
  const dots = rail ? rail.querySelector(".dots") : null;
  const label = rail ? rail.querySelector(".label span") : null;
  const labelBox = rail ? rail.querySelector(".label") : null;
  if (dots) {
    slides.forEach((s, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", "Ir a la sección " + (i + 1) + ": " + (s.dataset.titulo || ""));
      b.addEventListener("click", () => irA(i));
      dots.append(b);
    });
  }

  // Índice emergente.
  const indice = document.getElementById("indice");
  const lista = indice ? indice.querySelector("ol") : null;
  if (lista) {
    slides.forEach((s, i) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = "#" + s.id;
      const n = document.createElement("span");
      n.className = "n";
      n.textContent = String(i + 1).padStart(2, "0");
      a.append(n, document.createTextNode(s.dataset.titulo || s.id));
      a.addEventListener("click", (ev) => { ev.preventDefault(); indice.removeAttribute("open"); irA(i); });
      li.append(a);
      lista.append(li);
    });
  }
  document.querySelectorAll("[data-abrir-indice]").forEach((b) => b.addEventListener("click", () => indice && indice.setAttribute("open", "")));
  document.querySelectorAll("[data-cerrar-indice]").forEach((b) => b.addEventListener("click", () => indice && indice.removeAttribute("open")));
  if (indice) indice.addEventListener("click", (ev) => { if (ev.target === indice) indice.removeAttribute("open"); });

  // Sección actual: observador de intersección.
  let actual = 0;
  const progreso = document.querySelector(".progress");
  const menuLinks = [...document.querySelectorAll(".nav .menu a")];
  let listo = false; // hasta que el navegador haya saltado al #ancla inicial, no se reescribe la URL
  function marcar(i) {
    actual = i;
    const s = slides[i];
    if (dots) [...dots.children].forEach((b, j) => b.setAttribute("aria-current", String(i === j)));
    if (label) label.textContent = s.dataset.parte || "";
    if (labelBox) labelBox.style.top = (slides.length > 1 ? (i / (slides.length - 1)) * 100 : 0) + "%";
    if (progreso) progreso.style.width = ((i + 1) / slides.length) * 100 + "%";
    menuLinks.forEach((a) => a.setAttribute("aria-current", String(a.dataset.parte === s.dataset.parte)));
    if (listo && history.replaceState && s.id) history.replaceState(null, "", "#" + s.id);
  }
  const ioActual = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => { if (e.isIntersecting) marcar(slides.indexOf(e.target)); });
  }, { threshold: 0.5 });
  const ioReveal = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("on"); ioReveal.unobserve(e.target); } });
  }, { threshold: 0.15 });
  slides.forEach((s) => { ioActual.observe(s); ioReveal.observe(s); });

  function irA(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    slides[i].scrollIntoView({ behavior: reduce ? "instant" : "smooth", block: "start" });
  }

  // Teclado: flechas, espacio, inicio, fin, F para pantalla completa, I para el índice.
  window.addEventListener("keydown", (ev) => {
    if (ev.target.closest("input, textarea, button, a")) { if (ev.key !== "Escape") return; }
    if (indice && indice.hasAttribute("open")) {
      if (ev.key === "Escape") indice.removeAttribute("open");
      return;
    }
    switch (ev.key) {
      case "ArrowRight": case "ArrowDown": case "PageDown": case " ":
        ev.preventDefault(); irA(actual + 1); break;
      case "ArrowLeft": case "ArrowUp": case "PageUp":
        ev.preventDefault(); irA(actual - 1); break;
      case "Home": ev.preventDefault(); irA(0); break;
      case "End": ev.preventDefault(); irA(slides.length - 1); break;
      case "f": case "F":
        if (document.fullscreenElement) document.exitFullscreen(); else html.requestFullscreen && html.requestFullscreen();
        break;
      case "i": case "I":
        if (indice) indice.setAttribute("open", "");
        break;
    }
  });

  // Caja de órdenes con escritura automática.
  const typed = document.querySelector("[data-typed]");
  const nextEl = document.querySelector("[data-typed-next]");
  if (typed) {
    const frases = JSON.parse(typed.dataset.typed);
    let f = 0, pos = 0, borrando = false;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function pinta() { typed.textContent = frases[f].slice(0, pos); if (nextEl) nextEl.textContent = frases[(f + 1) % frases.length]; }
    function paso() {
      if (reduce) { pos = frases[f].length; pinta(); return; }
      if (!borrando) {
        pos++; pinta();
        if (pos >= frases[f].length) { borrando = true; setTimeout(paso, 2600); return; }
        setTimeout(paso, 38);
      } else {
        pos = Math.max(0, pos - 2); pinta();
        if (pos === 0) { borrando = false; f = (f + 1) % frases.length; setTimeout(paso, 250); return; }
        setTimeout(paso, 14);
      }
    }
    paso();
  }

  // Carrusel de pestañas: una a la izquierda cada 2,4 s.
  const car = document.querySelector(".carousel");
  if (car) {
    const strip = car.querySelector(".strip");
    const tabs = [...strip.children];
    let i = 0, timer = null;
    function ancho() { return tabs[0].getBoundingClientRect().width; }
    function pon(k) {
      i = k;
      strip.style.transform = "translateX(" + (-i * ancho()) + "px)";
      tabs.forEach((t, j) => { t.classList.toggle("act", j === i); t.classList.toggle("past", j < i); });
    }
    function avanza() {
      if (i >= tabs.length - 1) {
        // Vuelve al principio sin animar y sigue.
        strip.style.transition = "none"; pon(0);
        requestAnimationFrame(() => requestAnimationFrame(() => { strip.style.transition = ""; }));
        return;
      }
      pon(i + 1);
    }
    function arranca() { if (!timer) timer = setInterval(avanza, 2400); }
    function para() { clearInterval(timer); timer = null; }
    car.addEventListener("mouseenter", para);
    car.addEventListener("mouseleave", arranca);
    window.addEventListener("resize", () => pon(i));
    pon(0);
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) arranca();
  }

  // Citas de los heterónimos con flechas.
  const citas = document.querySelector(".citas");
  if (citas) {
    const datos = JSON.parse(citas.dataset.citas);
    const q = citas.querySelector(".q");
    const who = citas.querySelector(".who");
    let k = 0;
    function muestra(n) {
      citas.classList.add("fade");
      setTimeout(() => {
        k = (n + datos.length) % datos.length;
        q.textContent = datos[k].texto;
        q.lang = datos[k].lang || "es";
        who.textContent = datos[k].quien;
        citas.classList.remove("fade");
      }, 450);
    }
    citas.querySelector("[data-prev]").addEventListener("click", () => muestra(k - 1));
    citas.querySelector("[data-next]").addEventListener("click", () => muestra(k + 1));
    q.textContent = datos[0].texto; q.lang = datos[0].lang || "es"; who.textContent = datos[0].quien;
  }

  // Si la página se abre con #ancla, salta a esa sección sin animación una vez cargada;
  // antes de eso el carril no toca la URL, para que el navegador no acabe en la portada.
  const inicial = location.hash ? slides.findIndex((s) => "#" + s.id === location.hash) : -1;
  function saltarInicial() {
    if (inicial >= 0) { slides[inicial].scrollIntoView({ behavior: "instant", block: "start" }); marcar(inicial); }
    listo = true;
  }
  if (document.readyState === "complete") setTimeout(saltarInicial, 60);
  else window.addEventListener("load", () => setTimeout(saltarInicial, 60));
})();
