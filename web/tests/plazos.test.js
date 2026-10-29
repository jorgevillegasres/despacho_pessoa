const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const crearCalculadora = require("../assets/plazos.js");

const RAIZ = path.resolve(__dirname, "..", "..");
const festivos = JSON.parse(fs.readFileSync(path.join(RAIZ, "herramientas", "festivos_colombia.json"), "utf8"));
const calc = crearCalculadora(festivos);

test("petición del 25-sep-2026 vence el 19-oct-2026", () => {
  assert.equal(calc.calcularVencimiento("2026-09-25", 15).fechaVencimiento, "2026-10-19");
});

test("reclamo del 8-oct-2026 vence el 30-oct-2026 y cruza el festivo del 12", () => {
  const r = calc.calcularVencimiento("2026-10-08", 15);
  assert.equal(r.fechaVencimiento, "2026-10-30");
  assert.match(r.festivosCruzados.join(" "), /2026-10-12/);
});

test("48 horas desde el 9-oct-2026 vencen el 11-oct-2026", () => {
  assert.equal(calc.calcularVencimientoHoras("2026-10-09", 48).fechaVencimiento, "2026-10-11");
});

test("36 horas no se cuentan", () => {
  assert.throws(() => calc.calcularVencimientoHoras("2026-10-09", 36), /múltiplos de 24/);
});

test("inicio posterior al corte es error", () => {
  assert.throws(() => calc.textoReporte("peticion", "2026-11-05", "2026-10-30"), calc.ErrorDeEntrada);
});

test("año sin festivos es error", () => {
  assert.throws(() => calc.textoReporte("peticion", "2025-12-01", "2026-01-10"), /2025/);
});

test("plazo que cruza a 2028 es error", () => {
  assert.throws(() => calc.calcularVencimiento("2027-12-20", 15), /2028/);
});

test("radicación en sábado avisa", () => {
  assert.match(calc.textoReporte("peticion", "2026-10-10", "2026-10-30").texto, /AVISO: la fecha de radicación es inhábil/);
});

test("días personalizados menores que 1 son error", () => {
  assert.throws(() => calc.textoReporte("peticion", "2026-10-08", "2026-10-30", { diasPersonalizados: 0 }), /al menos 1/);
});

test("festivo guardado bajo otro año se rechaza", () => {
  assert.throws(() => crearCalculadora({ "2026": { "2027-01-01": "x" } }), /está bajo el año 2026/);
});

test("años cargados: 2026 y 2027", () => {
  assert.deepEqual(calc.aniosCargados(), [2026, 2027]);
});

test("calcularVencimiento rechaza n no entero o menor que 1", () => {
  for (const n of [NaN, 2.5, 0, -1, undefined, "3", Infinity]) {
    assert.throws(() => calc.calcularVencimiento("2026-10-08", n),
      { name: "Error", message: "el número de días hábiles debe ser al menos 1" }, String(n));
    assert.throws(() => calc.calcularVencimiento("2026-10-08", n), calc.ErrorDeEntrada, String(n));
  }
});

test("fechas mal formadas o inexistentes se rechazan con el texto de la terminal", () => {
  for (const f of ["2026-02-30", "2026-1-5", "", "2026-10-08x", undefined]) {
    const msg = `Fecha inválida '${f}'. Usa el formato ISO YYYY-MM-DD (ej. 2026-10-30).`;
    assert.throws(() => calc.calcularVencimiento(f, 3), { message: msg }, `venc ${f}`);
    assert.throws(() => calc.calcularVencimientoHoras(f, 48), { message: msg }, `horas ${f}`);
    assert.throws(() => calc.textoReporte("peticion", f, "2026-10-30"), { message: msg }, `inicio ${f}`);
    assert.throws(() => calc.textoReporte("peticion", "2026-10-08", f), { message: msg }, `corte ${f}`);
  }
  assert.throws(() => calc.calcularVencimiento("2026-02-30", 3), calc.ErrorDeEntrada);
});

test("días personalizados inválidos fallan antes que las fechas, con punto final", () => {
  for (const d of [0, -2, 2.5, NaN, "3"]) {
    assert.throws(() => calc.textoReporte("peticion", "2026-11-05", "2026-10-30", { diasPersonalizados: d }),
      { message: "el número de días hábiles debe ser al menos 1." }, String(d));
    assert.throws(() => calc.textoReporte("peticion", "basura", "2026-10-30", { diasPersonalizados: d }),
      { message: "el número de días hábiles debe ser al menos 1." }, String(d));
  }
});

test("modo desconocido se rechaza, incluso nombres heredados de Object", () => {
  for (const m of ["xyz", "constructor", "toString", "__proto__", undefined]) {
    assert.throws(() => calc.textoReporte(m, "2026-10-08", "2026-10-30"),
      { message: `modo desconocido: ${m}` }, String(m));
    assert.throws(() => calc.textoReporte(m, "2026-10-08", "2026-10-30"), calc.ErrorDeEntrada, String(m));
  }
});
