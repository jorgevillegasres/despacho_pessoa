# Materia: demanda laboral

**Tipo de documento:** demanda laboral.
**Plantilla:** `materias/demanda-laboral/plantillas/modelo-demanda-laboral.md`.
**Checklist:** `materias/demanda-laboral/checklist.md`.
**Plazos:** `materias/demanda-laboral/plazos.json` (con campos `null` y `revisar`: no se inventan términos).
**Corpus por defecto:** `fuentes/00_transversal`, `fuentes/02_laboral`.

## Para qué sirve

Es el segundo ejemplo del sistema. Sirve para mostrar que los mismos agentes pueden producir un documento distinto de una tutela, con otra plantilla, otra checklist y otro corpus.

## Cómo se usa

1. Crea un caso con `python herramientas/nuevo_caso.py --materia demanda-laboral`.
2. Carga la entrevista y las pruebas en `01-entrada/`.
3. Ajusta el corpus del caso en `00-expediente.md` si necesitas otras fuentes.
4. Ejecuta los agentes en orden.
5. Verifica la competencia, la caducidad/prescripción y los requisitos propios del caso antes de firmar.

## Límite

Este ejemplo no fija términos de caducidad ni de prescripción. Esos dependen del tipo de pretensión, de la fecha de los hechos y de la norma aplicable. El sistema debe calcularlos con la herramienta y el abogado debe verificarlos.
