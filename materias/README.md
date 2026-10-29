# Materias

Una **materia** es el tipo de actuación que el despacho produce: una tutela, una demanda laboral, un concepto, un recurso, un contrato. No es la rama del derecho; es el **molde de salida** y su lista de control.

La idea es simple:

- Los **agentes** son los mismos para todas las materias.
- La **biblioteca** (`fuentes/`) es compartida.
- La **materia** aporta lo que cambia: la plantilla del documento, la checklist procesal, los plazos y el corpus por defecto.
- El **caso** (`casos/<caso>/00-expediente.md`) dice qué materia usa, qué corpus concreto lee y dónde están sus archivos.

```text
materias/
├── tutela/
│   ├── materia.json
│   ├── checklist.md
│   ├── plazos.json
│   └── README.md
├── demanda-laboral/
│   ├── materia.json
│   ├── checklist.md
│   ├── plazos.json
│   ├── plantillas/modelo-demanda-laboral.md
│   └── README.md
├── derecho-de-peticion/
│   ├── materia.json
│   ├── checklist.md
│   ├── plazos.json
│   ├── plantillas/modelo-derecho-de-peticion.md
│   └── README.md
└── README.md
```

## Cómo se crea una materia nueva

1. Copia una carpeta existente (`materias/tutela/` o `materias/demanda-laboral/`) y renómbrala con el identificador de la nueva materia, por ejemplo `concepto-juridico`.
2. Edita `materia.json`: cambia `id`, `nombre`, `descripcion`, `tipo_documento`, `plantilla`, `checklist`, `plazos` y `corpus_por_defecto`.
3. Escribe la plantilla del documento en `plantillas/`.
4. Escribe la checklist procesal en `checklist.md`.
5. Configura los plazos en `plazos.json`. Si no estás seguro de un término, déjalo en `null` y escribe `revisar`; el sistema no debe inventar plazos.
6. Crea un caso con `python herramientas/nuevo_caso.py --materia <id>` o copia `casos/_PLANTILLA-CASO/`.

## Regla de oro

La materia es una **plantilla de trabajo**, no un concepto jurídico. Cada término, requisito y plazo debe verificarse en la norma vigente y en la fuente oficial. El sistema organiza; el abogado decide.
