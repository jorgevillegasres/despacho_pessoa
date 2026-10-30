# Materia: derecho de petición

Escrito de petición ante una autoridad o un particular. En el despacho suele ser el primer documento de un caso de salud, laboral o de habeas data, y la prueba de su radicación es lo que después sostiene la inmediatez y la subsidiariedad de una tutela.

## Qué trae

- `materia.json`: configuración. Corpus por defecto `fuentes/00_transversal/`; añade en el expediente la carpeta de la materia de fondo (`01_salud/`, `02_laboral/` o `03_habeas_data/`).
- `plantillas/modelo-derecho-de-peticion.md`: la estructura, en el orden hechos, peticiones, fundamentos y término.
- `checklist.md`: la lista de control del Redactor y del Verificador.
- `plazos.json`: los tres términos de respuesta, que la calculadora ya conoce (`peticion`, `peticion_docs`, `peticion_consulta`).

## Lo que hay que saber antes de usarla

- La estructura y las reglas de redacción (una petición por punto, modalidad desde la primera línea, término en sección propia, anexos siempre, advertencia de tutela como última línea) vienen de un método de redacción consultado el 29 de octubre de 2026.
- Solo se citan las normas que están en el corpus: artículo 23 de la Constitución y artículos 13, 14 y 32 de la Ley 1755 de 2015, más la jurisprudencia sobre respuesta de fondo. Las reglas marcadas «verificar» en la checklist tienen artículo en la ley pero todavía no están copiadas en `fuentes/`: incorporarlas antes de citarlas.
- El plazo se calcula con la herramienta. Si la petición ya se radicó, la fecha de radicación es un hecho probado y la calculadora dice cuándo vence.

## Crear un caso con esta materia

```text
python herramientas/nuevo_caso.py --materia derecho-de-peticion --nombre "Petición a la EPS"
```
