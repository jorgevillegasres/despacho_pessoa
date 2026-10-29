/* Calculadora de plazos del Despacho Pessoa, versión navegador.
   Misma lógica y mismo texto que herramientas/calcular_plazos.py: la prueba
   herramientas/tests/test_paridad_web.py compara las dos salidas día por día.
   Si cambias una, cambia la otra. Fechas siempre como texto ISO (AAAA-MM-DD). */
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) module.exports = fabrica;
  else raiz.crearCalculadora = fabrica;
})(typeof self !== "undefined" ? self : this, function crearCalculadora(datosFestivos) {
  class ErrorDeEntrada extends Error {}

  const hoyIso = () => {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const dia = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${dia}`;
  };
  const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
  // [cantidad, descripción, unidad] — idéntico a MODOS_PLAZO en calcular_plazos.py
  const MODOS = {
    peticion: [15, "Derecho de Petición General / Reclamo Habeas Data (Art. 14 Ley 1755 de 2015 / Art. 16 Ley 1266 de 2008)", "habiles"],
    peticion_docs: [10, "Petición de Documentos e Información / Historia Clínica (Art. 14 núm. 1 Ley 1755 de 2015)", "habiles"],
    peticion_consulta: [30, "Petición de Consulta (Art. 14 núm. 2 Ley 1755 de 2015)", "habiles"],
    fallo_tutela: [10, "Término para fallar Acción de Tutela (Art. 86 CP / Art. 29 Decreto 2591 de 1991)", "habiles"],
    impugnacion: [3, "Término para impugnar el fallo de tutela (Art. 31 Decreto 2591 de 1991)", "habiles"],
    cumplimiento_48h: [48, "Cumplimiento de orden de tutela en 48 horas (Art. 27 Decreto 2591 de 1991)", "horas"],
  };

  const aFecha = (iso) => {
    const [a, m, d] = iso.split("-").map(Number);
    return new Date(Date.UTC(a, m - 1, d));
  };
  const aIso = (f) => f.toISOString().slice(0, 10);
  const sumarDias = (iso, n) => {
    const f = aFecha(iso);
    f.setUTCDate(f.getUTCDate() + n);
    return aIso(f);
  };
  const diaSemana = (iso) => (aFecha(iso).getUTCDay() + 6) % 7; // 0 = lunes, como en Python
  const nombreDia = (iso) => DIAS[diaSemana(iso)];
  const diferenciaDias = (desde, hasta) => Math.round((aFecha(hasta) - aFecha(desde)) / 86400000);
  const anio = (iso) => Number(iso.slice(0, 4));

  const festivos = new Map();
  const anios = new Set();
  for (const [clave, dias] of Object.entries(datosFestivos)) {
    if (clave.startsWith("_")) continue;
    anios.add(Number(clave));
    for (const [iso, nombre] of Object.entries(dias)) {
      if (anio(iso) !== Number(clave)) {
        throw new ErrorDeEntrada(`La fecha ${iso} está bajo el año ${clave} en festivos_colombia.json.`);
      }
      festivos.set(iso, nombre);
    }
  }
  const aniosCargados = () => [...anios].sort((a, b) => a - b);

  function esDiaHabil(iso) {
    if (diaSemana(iso) === 5) return [false, "Sábado (inhábil)"];
    if (diaSemana(iso) === 6) return [false, "Domingo (inhábil)"];
    if (festivos.has(iso)) return [false, `Festivo en Colombia: ${festivos.get(iso)}`];
    return [true, "Día hábil"];
  }

  function exigirFechaIso(s) {
    if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s) || aIso(aFecha(s)) !== s) {
      throw new ErrorDeEntrada(`Fecha inválida '${s}'. Usa el formato ISO YYYY-MM-DD (ej. 2026-10-30).`);
    }
  }

  function exigirDiasHabiles(n, punto) {
    if (!Number.isInteger(n) || n < 1) {
      throw new ErrorDeEntrada(`el número de días hábiles debe ser al menos 1${punto}`);
    }
  }

  function validarFechas(inicio, corte) {
    exigirFechaIso(inicio);
    exigirFechaIso(corte);
    for (const f of [inicio, corte]) {
      if (!anios.has(anio(f))) {
        throw new ErrorDeEntrada(
          `No tengo festivos cargados para el año ${anio(f)}. Años disponibles: ` +
          `${aniosCargados().join(", ")}. Añádelos en herramientas/festivos_colombia.json.`);
      }
    }
    if (inicio > corte) {
      throw new ErrorDeEntrada(
        `La fecha de inicio (${inicio}) es posterior a la fecha de corte (${corte}). Revisa las fechas.`);
    }
  }

  function calcularVencimientoHoras(inicio, horas) {
    exigirFechaIso(inicio);
    if (horas % 24) {
      throw new ErrorDeEntrada(
        "esta herramienta solo cuenta plazos en horas que sean múltiplos de 24; " +
        "para otros usa fecha y hora exactas");
    }
    const venc = sumarDias(inicio, horas / 24);
    if (!anios.has(anio(venc))) {
      throw new ErrorDeEntrada(
        `El plazo cruza al año ${anio(venc)} y no tengo sus festivos. ` +
        "Añádelos en herramientas/festivos_colombia.json.");
    }
    return {
      fechaVencimiento: venc,
      nota: "Plazo en horas corridas. Si la orden fija otra forma de contar, prevalece la orden. " +
            "El estado tiene granularidad de día (no se compara la hora).",
    };
  }

  function calcularVencimiento(inicio, n) {
    exigirDiasHabiles(n, "");
    exigirFechaIso(inicio);
    if (!anios.has(anio(inicio))) throw new ErrorDeEntrada(`No tengo festivos cargados para el año ${anio(inicio)}.`);
    let cursor = inicio;
    let conteo = 0;
    const detalle = [];
    const festivosCruzados = [];
    while (conteo < n) {
      cursor = sumarDias(cursor, 1);
      if (!anios.has(anio(cursor))) {
        throw new ErrorDeEntrada(
          `El plazo cruza al año ${anio(cursor)} y no tengo sus festivos. ` +
          "Añádelos en herramientas/festivos_colombia.json.");
      }
      if (esDiaHabil(cursor)[0]) {
        conteo += 1;
        detalle.push(`  Día hábil #${String(conteo).padStart(2, "0")}: ${cursor} (${nombreDia(cursor)})`);
      } else if (festivos.has(cursor)) {
        festivosCruzados.push(`${cursor} (${festivos.get(cursor)})`);
      }
    }
    return { fechaVencimiento: cursor, detalle, festivosCruzados };
  }

  function contarTranscurridos(inicio, corte) {
    if (corte <= inicio) return { habiles: 0, calendario: diferenciaDias(inicio, corte) };
    let cursor = inicio;
    let habiles = 0;
    while (cursor < corte) {
      cursor = sumarDias(cursor, 1);
      if (esDiaHabil(cursor)[0]) habiles += 1;
    }
    return { habiles, calendario: diferenciaDias(inicio, corte) };
  }

  /* Devuelve {texto, vencimiento, estado}. `texto` es, línea por línea, lo que imprime
     calcular_plazos.py con los mismos argumentos. */
  function textoReporte(modo, inicio, corte, opciones = {}) {
    const diasPersonalizados = opciones.diasPersonalizados == null ? null : opciones.diasPersonalizados;
    const detalle = opciones.detalle !== false;
    const cortePorDefecto = opciones.cortePorDefecto === true;
    if (!Object.prototype.hasOwnProperty.call(MODOS, modo)) {
      throw new ErrorDeEntrada(`modo desconocido: ${modo}`);
    }
    if (diasPersonalizados !== null) exigirDiasHabiles(diasPersonalizados, ".");
    validarFechas(inicio, corte);
    let [cantidad, descripcion, unidad] = MODOS[modo];
    if (diasPersonalizados !== null) {
      cantidad = diasPersonalizados;
      unidad = "habiles";
      descripcion = `Plazo personalizado de ${cantidad} días hábiles`;
    }
    const igual = "=".repeat(78);
    const guion = "-".repeat(78);
    const a = aniosCargados();
    const titulo = `CALCULADORA DETERMINÍSTICA DE PLAZOS — DESPACHO PESSOA (COLOMBIA, festivos ${a[0]}-${a[a.length - 1]})`;
    const etiqueta = cortePorDefecto ? " (fecha de referencia por defecto)" : "";
    const cabecera = [
      `Norma / Modo aplicado     : ${descripcion}`,
      `Fecha de radicación/hito  : ${inicio} (${nombreDia(inicio)})`,
      `Fecha de corte / consulta : ${corte} (${nombreDia(corte)})${etiqueta}`,
    ];

    if (unidad === "horas") {
      const r = calcularVencimientoHoras(inicio, cantidad);
      const v = r.fechaVencimiento;
      const estado = corte > v ? "VENCIDO (el término se cumplió antes de la fecha de corte)"
        : corte === v ? "EN CURSO — vence hoy, a la hora de la notificación" : "EN CURSO";
      const lineas = [igual, titulo, igual, ...cabecera,
        `Término exigido           : ${cantidad} horas corridas`, guion,
        `FECHA EXACTA VENCIMIENTO  : ${v} (${nombreDia(v)}) a la misma hora de la notificación`,
        `ESTADO DEL TÉRMINO        : ${estado}`,
        `Nota                      : ${r.nota}`, igual];
      return { texto: lineas.join("\n"), vencimiento: v, estado };
    }

    const r = calcularVencimiento(inicio, cantidad);
    const t = contarTranscurridos(inicio, corte);
    const v = r.fechaVencimiento;
    const estado = corte > v ? "VENCIDO (el término se cumplió antes de la fecha de corte)"
      : corte === v ? "EN CURSO — vence hoy" : `EN CURSO — faltan ${cantidad - t.habiles} día(s) hábil(es)`;
    const lineas = [igual, titulo, igual, ...cabecera,
      `Término exigido           : ${cantidad} días hábiles`,
      "Regla de cómputo          : inicia el día hábil siguiente a la radicación (Art. 62 Ley 4ª de 1913; CGP art. 118) [referencia de la herramienta: no es cita del corpus]"];
    const [habilInicio, motivoInicio] = esDiaHabil(inicio);
    if (!habilInicio) {
      lineas.push(`AVISO: la fecha de radicación es inhábil (${motivoInicio}). Esta calculadora cuenta desde el primer día ` +
        "hábil siguiente; si el despacho la tiene por recibida el siguiente día hábil, el vencimiento corre un día más. " +
        "Decisión del abogado.");
    }
    lineas.push(
      `Festivos en el período    : ${r.festivosCruzados.length ? r.festivosCruzados.join(", ") : "Ninguno"}`,
      guion,
      `FECHA EXACTA VENCIMIENTO  : ${v} (${nombreDia(v)}) — vence en esta fecha`,
      `Días transcurridos al corte: ${t.habiles} días hábiles (${t.calendario} días calendario)`,
      `ESTADO DEL TÉRMINO        : ${estado}`,
      "Nota: la hora límite depende del canal y del despacho (CGP art. 109); esta herramienta cuenta fechas, no horas. [referencia de la herramienta: no es cita del corpus]",
      guion);
    if (detalle) {
      lineas.push("Desglose día a día hábil (el conteo inicia el día hábil siguiente a la radicación):", ...r.detalle, igual);
    }
    return { texto: lineas.join("\n"), vencimiento: v, estado };
  }

  return {
    ErrorDeEntrada, hoy: hoyIso, MODOS, aniosCargados, esDiaHabil,
    calcularVencimiento, calcularVencimientoHoras, contarTranscurridos, textoReporte,
  };
});
