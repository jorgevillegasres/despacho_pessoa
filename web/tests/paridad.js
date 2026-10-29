// Puente para herramientas/tests/test_paridad_web.py: lee casos en JSON por la entrada
// estándar y devuelve, en el mismo orden, lo que calcula web/assets/plazos.js.
const fs = require("node:fs");
const path = require("node:path");
const crearCalculadora = require("../assets/plazos.js");

const RAIZ = path.resolve(__dirname, "..", "..");
const calc = crearCalculadora(JSON.parse(
  fs.readFileSync(path.join(RAIZ, "herramientas", "festivos_colombia.json"), "utf8")));
const casos = JSON.parse(fs.readFileSync(0, "utf8"));

const resultados = casos.map((c) => {
  try {
    if (c.tipo === "vencimiento") {
      const r = calc.calcularVencimiento(c.inicio, c.n);
      return { vencimiento: r.fechaVencimiento, festivos: r.festivosCruzados };
    }
    const r = calc.textoReporte(c.modo, c.inicio, c.corte, {
      diasPersonalizados: c.dias, detalle: c.detalle, cortePorDefecto: c.cortePorDefecto,
    });
    return { texto: r.texto };
  } catch (e) {
    if (e instanceof calc.ErrorDeEntrada) return { error: e.message };
    throw e;
  }
});
process.stdout.write(JSON.stringify(resultados));
