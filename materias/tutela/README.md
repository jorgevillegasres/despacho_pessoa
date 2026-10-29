# Materia: tutela

**Tipo de documento:** acción de tutela.
**Plantilla:** `plantillas/modelo-tutela.md`.
**Checklist:** `materias/tutela/checklist.md`.
**Plazos:** `materias/tutela/plazos.json`.
**Corpus por defecto:** `fuentes/00_transversal`; el caso añade la carpeta de su área (salud, laboral, habeas data, etc.).

## Cómo se usa

1. Crea un caso con `python herramientas/nuevo_caso.py --materia tutela`.
2. En `casos/<caso>/00-expediente.md`, escribe el corpus concreto del caso. Por ejemplo:
   - Salud: `fuentes/00_transversal, fuentes/01_salud`.
   - Laboral: `fuentes/00_transversal, fuentes/02_laboral`.
   - Habeas data: `fuentes/00_transversal, fuentes/03_habeas_data`.
3. Carga la entrevista y las pruebas en `01-entrada/`.
4. Ejecuta los agentes en orden: Recepción → Investigador → Redactor → Verificador → Contraparte.
5. Revisa la checklist antes de firmar.

## Ejemplo trabajado

Esta versión pública no trae un caso resuelto. Para ver el flujo completo, crea tu propio caso con `python herramientas/nuevo_caso.py --materia tutela` y sigue las guías de `docs/guias/`. La carpeta `casos/_PLANTILLA-CASO/` muestra la estructura que tendrá.

## Límite

La checklist y los plazos son una guía de trabajo. Verifica siempre la norma vigente, la competencia y el caso concreto. La tutela no es un formato universal: cambia según el derecho fundamental, la autoridad accionada y la urgencia.
