# Corpus cerrado del despacho

Solo existe jurídicamente lo que está aquí (Regla 1 del Estatuto). Cada archivo declara en su cabecera:
- **Tipo de contenido:** `literal` (texto oficial copiado), `extracto` (fragmentos oficiales seleccionados), `resumen` (paráfrasis: no citable entre comillas) o `distractor` (material de estudio con tesis superadas; nunca citable).
- **Fecha de consulta de la fuente oficial.** Es la fecha de la última consulta al sitio oficial. El estado de cotejo se registra en `00-indice.md`: `Cotejado` significa que el texto se comparó con la fuente oficial; `Consulta registrada` significa que la fuente se consultó, pero el cotejo literal queda pendiente de revisión.

El **catálogo** de la biblioteca está en `00-indice.md`: una fila por fuente, con tipo, identificador, materia, problema jurídico, estado y si es citable. Úsalo antes de abrir los archivos.

Los archivos con prefijo `DISTRACTOR-` están aquí a propósito, para entrenar el criterio del Investigador. No se citan.

`SELLO.json` guarda la huella SHA-256 de cada archivo. Antes y después de cada ejecución:

    python herramientas/verificar_corpus.py --comprobar

Si cambias el corpus a propósito, vuelve a sellar (`python herramientas/verificar_corpus.py --sellar`) y anótalo en `registro.md`.
