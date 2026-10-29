// ARCHIVO GENERADO por web/generar_datos_web.py desde herramientas/festivos_colombia.json,
// despacho/agentes/*.md y despacho/permisos.json. No editar a mano.
window.DESPACHO = {
  "festivos": {
    "_fuente": "Ley 51 de 1983 (Ley Emiliani). Verificar cada año contra el calendario oficial antes de usar.",
    "_pendiente_decision_abogado": "Prensa reporta la Ley 2578 del 1-jun-2026 (festivo Virgen de Chiquinquirá, 9 de julio, trasladado al lunes: 2026-07-13 y 2027-07-12). No está incorporada aquí porque su vigencia y su encaje en la Ley 51 de 1983 están en discusión (demanda ante la Corte Constitucional). El Socio Director decide si se añade tras verificar el Diario Oficial.",
    "2026": {
      "2026-01-01": "Año Nuevo",
      "2026-01-12": "Reyes Magos (trasladado al lunes)",
      "2026-03-23": "San José (trasladado al lunes)",
      "2026-04-02": "Jueves Santo",
      "2026-04-03": "Viernes Santo",
      "2026-05-01": "Día del Trabajo",
      "2026-05-18": "Ascensión del Señor (trasladado al lunes)",
      "2026-06-08": "Corpus Christi (trasladado al lunes)",
      "2026-06-15": "Sagrado Corazón (trasladado al lunes)",
      "2026-06-29": "San Pedro y San Pablo",
      "2026-07-20": "Independencia de Colombia",
      "2026-08-07": "Batalla de Boyacá",
      "2026-08-17": "Asunción de la Virgen (trasladado al lunes)",
      "2026-10-12": "Día de la Raza / Diversidad Étnica y Cultural",
      "2026-11-02": "Todos los Santos (trasladado al lunes)",
      "2026-11-16": "Independencia de Cartagena (trasladado al lunes)",
      "2026-12-08": "Inmaculada Concepción",
      "2026-12-25": "Navidad"
    },
    "2027": {
      "2027-01-01": "Año Nuevo",
      "2027-01-11": "Reyes Magos (trasladado al lunes)",
      "2027-03-22": "San José (trasladado al lunes)",
      "2027-03-25": "Jueves Santo",
      "2027-03-26": "Viernes Santo",
      "2027-05-01": "Día del Trabajo",
      "2027-05-10": "Ascensión del Señor (trasladado al lunes)",
      "2027-05-31": "Corpus Christi (trasladado al lunes)",
      "2027-06-07": "Sagrado Corazón (trasladado al lunes)",
      "2027-07-05": "San Pedro y San Pablo (trasladado al lunes)",
      "2027-07-20": "Independencia de Colombia",
      "2027-08-07": "Batalla de Boyacá",
      "2027-08-16": "Asunción de la Virgen (trasladado al lunes)",
      "2027-10-18": "Día de la Raza / Diversidad Étnica y Cultural (trasladado al lunes)",
      "2027-11-01": "Todos los Santos",
      "2027-11-15": "Independencia de Cartagena (trasladado al lunes)",
      "2027-12-08": "Inmaculada Concepción",
      "2027-12-25": "Navidad"
    }
  },
  "agentes": [
    {
      "id": "01-observador-caeiro",
      "nombre": "El Observador",
      "heteronimo": "Alberto Caeiro",
      "descripcion": "Recepción y archivista de hechos puros. Ordena cronológicamente lo probado y marca NO CONSTA lo que carece de soporte documental.",
      "cita": "Lo que vemos de las cosas son las cosas.",
      "produce": "hechos.md",
      "falla": "La empatía: dar por probado lo que el cliente cuenta con convicción pero no aporta.",
      "lee": [
        "ESTATUTO.md",
        "casos/*/00-expediente.md",
        "casos/*/01-entrada/**",
        "materias/**"
      ],
      "escribe": [
        "casos/*/02-hechos/hechos.md"
      ],
      "ejecuta": [
        "herramientas/calcular_plazos.py"
      ]
    },
    {
      "id": "02-investigador-search",
      "nombre": "El Investigador",
      "heteronimo": "Alexander Search",
      "descripcion": "Investigador de corpus cerrado. Localiza normas y sentencias únicamente dentro de fuentes/ y construye fichas de cita textuales.",
      "cita": "Busco únicamente dentro de los límites de lo que está escrito y verificado.",
      "produce": "investigacion.md",
      "falla": "Parafrasear una cita en lugar de copiarla letra por letra, o quedarte con el primer documento que encuentras sin leer los demás de la misma carpeta.",
      "lee": [
        "ESTATUTO.md",
        "casos/*/00-expediente.md",
        "casos/*/02-hechos/hechos.md",
        "materias/**",
        "fuentes/**",
        "plantillas/ficha-cita.md"
      ],
      "escribe": [
        "casos/*/03-investigacion/investigacion.md"
      ],
      "ejecuta": []
    },
    {
      "id": "03-redactor-reis",
      "nombre": "El Redactor",
      "heteronimo": "Ricardo Reis",
      "descripcion": "Redactor formal del documento del caso. Ensambla borrador.md únicamente con hechos.md, investigacion.md y la plantilla de la materia, sin añadir un hecho ni una cita propia.",
      "cita": "Sabio es quien se contenta con el espectáculo del mundo.",
      "produce": "borrador.md",
      "falla": "Adornar: añadir una cita \"que todo el mundo conoce\", redondear una fecha, convertir un NO CONSTA en afirmación.",
      "lee": [
        "ESTATUTO.md",
        "casos/*/00-expediente.md",
        "casos/*/02-hechos/hechos.md",
        "casos/*/03-investigacion/investigacion.md",
        "materias/**",
        "plantillas/**"
      ],
      "escribe": [
        "casos/*/04-borrador/borrador.md"
      ],
      "ejecuta": []
    },
    {
      "id": "04-verificador-soares",
      "nombre": "El Verificador",
      "heteronimo": "Bernardo Soares",
      "descripcion": "Auditor de citas, fechas y hechos. Coteja el borrador contra el corpus del expediente y hechos.md, ítem por ítem. Nunca reescribe el borrador.",
      "cita": "La exactitud de la partida doble es mi moral.",
      "produce": "informe-verificacion.md",
      "falla": "La complacencia: dar por buena una cita \"parecida\" sin abrir el archivo.",
      "lee": [
        "ESTATUTO.md",
        "casos/*/00-expediente.md",
        "casos/*/04-borrador/borrador.md",
        "casos/*/02-hechos/hechos.md",
        "casos/*/03-investigacion/investigacion.md",
        "casos/*/01-entrada/**",
        "materias/**",
        "fuentes/**",
        "plantillas/ficha-cita.md"
      ],
      "escribe": [
        "casos/*/05-auditoria/informe-verificacion.md"
      ],
      "ejecuta": [
        "herramientas/verificar_citas.py",
        "herramientas/calcular_plazos.py"
      ]
    },
    {
      "id": "05-diablo-campos",
      "nombre": "El Abogado del Diablo",
      "heteronimo": "Álvaro de Campos",
      "descripcion": "Contradictor procesal. Ataca el borrador como lo haría la contraparte o un juez estricto y califica el riesgo de improcedencia.",
      "cita": "Soy lúcido e implacable.",
      "produce": "informe-riesgo.md",
      "falla": "Criticar por deporte o exigir requisitos que el propio corpus dice que no se exigen.",
      "lee": [
        "ESTATUTO.md",
        "casos/*/00-expediente.md",
        "casos/*/04-borrador/borrador.md",
        "casos/*/02-hechos/hechos.md",
        "casos/*/01-entrada/**",
        "casos/*/05-auditoria/informe-verificacion.md",
        "materias/**",
        "fuentes/**"
      ],
      "escribe": [
        "casos/*/05-auditoria/informe-riesgo.md"
      ],
      "ejecuta": []
    }
  ]
};
